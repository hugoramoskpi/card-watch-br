import json
import re
import uuid

from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage

from ..state import AgentState, CardBuzz
from ...tools.reddit_tool import search_reddit_for_black_cards
from ...tools.brave_tool import search_brave_for_promotions


def discovery_node(state: AgentState) -> AgentState:
    llm = ChatAnthropic(model="claude-sonnet-4-6")

    reddit_results = search_reddit_for_black_cards.invoke(
        {"query": "cartão black premium promoção 2026"}
    )
    brave_results = search_brave_for_promotions.invoke(
        {"query": "cartão crédito black premium promoção aprovação anuidade brasil 2026"}
    )

    text_lines = [
        f"- {r['title']}: {r.get('description', '') or r.get('text', '')}"
        for r in reddit_results + brave_results
    ]
    all_text = "\n".join(text_lines) or "Sem menções encontradas"

    response = llm.invoke([HumanMessage(content=f"""Analise as menções abaixo de cartões de crédito premium/black encontradas hoje.
Liste APENAS os cartões premium/black distintos mencionados com promoções ou buzz positivo.
Inclua qualquer cartão premium mencionado — não se limite a uma lista fixa.

Menções encontradas hoje:
{all_text}

Responda SOMENTE em JSON válido, sem markdown nem explicações:
{{"cards": [{{"card_name": "Nome Completo do Cartão", "buzz_score": 8, "mentions_count": 3, "sources": ["Reddit r/investimentos"]}}]}}

Se não houver menções relevantes, retorne: {{"cards": []}}""")])

    match = re.search(r'\{.*\}', response.content, re.DOTALL)
    try:
        data: dict = json.loads(match.group()) if match else {"cards": []}
    except json.JSONDecodeError:
        data = {"cards": []}

    return {
        **state,
        "cycle_id": str(uuid.uuid4()),
        "discovered_cards": data.get("cards", []),
    }
