import logging
import os
import uuid
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from src.db.database import SessionLocal
from src.db.repository import get_promotions
from src.agent.graph import build_graph
from src.agent.state import AgentState

logger = logging.getLogger(__name__)

def format_status_message(cards_found: int, promos_validated: int, alerts_sent: int) -> str:
    return (
        f"*Status do último ciclo*\n\n"
        f"Cartões encontrados: *{cards_found}*\n"
        f"Promoções validadas: *{promos_validated}*\n"
        f"Alertas enviados: *{alerts_sent}*"
    )

def format_promo_list(promos: list[dict]) -> str:
    if not promos:
        return "Nenhuma promoção ativa no momento."
    conf_label = {1: "Baixa", 2: "Média", 3: "Alta"}
    lines = []
    for p in promos[:5]:
        label = conf_label.get(p.get("confidence", 1), "")
        lines.append(f"*{p['card_name']}* ({label})\n  {p['summary']}")
    return "\n\n".join(lines)

async def cmd_status(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        format_status_message(0, 0, 0),
        parse_mode="Markdown"
    )

async def cmd_promos(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    db = SessionLocal()
    try:
        promos = get_promotions(db)
        promo_dicts = [
            {"card_name": p.card_name, "summary": p.summary, "confidence": p.confidence}
            for p in promos
        ]
        await update.message.reply_text(format_promo_list(promo_dicts), parse_mode="Markdown")
    finally:
        db.close()

async def cmd_buscar(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("Iniciando busca... Pode levar alguns minutos.")
    graph = build_graph()
    initial: AgentState = {
        "cycle_id": str(uuid.uuid4()),
        "discovered_cards": [],
        "raw_promos": [],
        "validated_promos": [],
        "alerts_sent": [],
    }
    result = graph.invoke(initial)
    await update.message.reply_text(
        format_status_message(
            len(result["discovered_cards"]),
            len(result["validated_promos"]),
            len(result["alerts_sent"]),
        ),
        parse_mode="Markdown"
    )

def create_bot() -> Application:
    token = os.environ["TELEGRAM_BOT_TOKEN"]
    app = Application.builder().token(token).build()
    app.add_handler(CommandHandler("status", cmd_status))
    app.add_handler(CommandHandler("promos", cmd_promos))
    app.add_handler(CommandHandler("buscar", cmd_buscar))
    return app

if __name__ == "__main__":
    create_bot().run_polling()
