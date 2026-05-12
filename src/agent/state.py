from typing import TypedDict


class CardBuzz(TypedDict):
    card_name: str
    buzz_score: int
    mentions_count: int
    sources: list[str]


class RawPromo(TypedDict):
    card_name: str
    text: str
    url: str
    source_name: str


class ValidatedPromo(TypedDict):
    card_name: str
    summary: str
    urls: list[str]
    confidence: int  # 1=baixo, 2=médio, 3=alto
    sources: list[str]


class AgentState(TypedDict):
    cycle_id: str
    discovered_cards: list[CardBuzz]
    raw_promos: list[RawPromo]
    validated_promos: list[ValidatedPromo]
    alerts_sent: list[str]
