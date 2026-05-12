import asyncio
import logging
import os
import telegram
from ..state import AgentState
from ...db.database import SessionLocal
from ...db.repository import upsert_promotion, mark_alerted

logger = logging.getLogger(__name__)


def _send_telegram_alert(promo_summary: str, card_name: str, confidence: int, urls: list[str]) -> None:
    token = os.environ.get("TELEGRAM_BOT_TOKEN", "")
    chat_id = os.environ.get("TELEGRAM_CHAT_ID", "")
    if not token or not chat_id:
        logger.warning("Telegram não configurado — alerta suprimido")
        return

    conf_label = {1: "🔴 Baixa", 2: "🟡 Média", 3: "🟢 Alta"}.get(confidence, "🔵")
    sources_text = "\n".join(f"  • {u}" for u in urls[:3])
    message = (
        f"🃏 *CARD WATCH BR — Nova Promoção!*\n\n"
        f"📌 *Cartão:* {card_name}\n"
        f"💬 {promo_summary}\n"
        f"✅ Confiança: {conf_label}\n\n"
        f"📎 Fontes:\n{sources_text}"
    )

    async def _send():
        bot = telegram.Bot(token=token)
        await bot.send_message(chat_id=chat_id, text=message, parse_mode="Markdown")

    try:
        asyncio.run(_send())
    except Exception as e:
        logger.error("Erro ao enviar alerta Telegram: %s", e)


def persist_alert_node(state: AgentState) -> AgentState:
    alerts_sent: list[str] = []
    db = SessionLocal()
    try:
        for promo in state["validated_promos"]:
            saved, is_new = upsert_promotion(
                db,
                card_name=promo["card_name"],
                summary=promo["summary"],
                sources=promo["sources"],
                confidence=promo["confidence"],
                raw_urls=promo["urls"],
            )
            if is_new:
                _send_telegram_alert(promo["summary"], promo["card_name"], promo["confidence"], promo["urls"])
                mark_alerted(db, saved.id)
                alerts_sent.append(saved.id)
    finally:
        db.close()

    return {**state, "alerts_sent": alerts_sent}
