import json
import os
import re
from collections import defaultdict
from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage
from ..state import AgentState, RawPromo, ValidatedPromo

_MIN_SOURCES = int(os.getenv("MIN_SOURCES_TO_VALIDATE", "2"))


def cross_validate_node(state: AgentState) -> AgentState:
    if not state["raw_promos"]:
        return {**state, "validated_promos": []}

    by_card: dict[str, list[RawPromo]] = defaultdict(list)
    for promo in state["raw_promos"]:
        by_card[promo["card_name"]].append(promo)

    candidates = []
    for card_name, promos in by_card.items():
        unique_sources = list({p["source_name"] for p in promos})
        if len(unique_sources) >= _MIN_SOURCES:
            candidates.append({
                "card_name": card_name,
                "texts": [p["text"] for p in promos],
                "urls": [p["url"] for p in promos],
                "sources": unique_sources,
            })

    if not candidates:
        return {**state, "validated_promos": []}

    llm = ChatAnthropic(model="claude-sonnet-4-6")
    prompt_data = json.dumps(candidates, ensure_ascii=False)
    response = llm.invoke([HumanMessage(content=f"""Analise as seguintes promoções de cartões premium/black coletadas de múltiplas fontes.
Para cada grupo, gere um resumo claro e objetivo da promoção em português.
Atribua confidence: 1 (1 fonte), 2 (2 fontes), 3 (3+ fontes).

Dados:
{prompt_data}

Responda SOMENTE em JSON válido sem markdown:
[{{"card_name": "...", "summary": "Resumo claro da promoção", "confidence": 2, "urls": [...], "sources": [...]}}]

Se nenhuma promoção for legítima, retorne: []""")])

    match = re.search(r'\[.*\]', response.content, re.DOTALL)
    try:
        validated: list[ValidatedPromo] = json.loads(match.group()) if match else []
    except json.JSONDecodeError:
        validated = []

    return {**state, "validated_promos": validated}
