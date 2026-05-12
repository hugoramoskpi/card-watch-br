from ..state import AgentState, RawPromo
from ...tools.reddit_tool import search_reddit_for_black_cards
from ...tools.brave_tool import search_brave_for_promotions
from ...tools.scraper_tool import scrape_hardmob_for_black_cards

_PROMO_KEYWORDS = [
    "promoção", "promocao", "anuidade", "aprovado", "aprovação",
    "bônus", "bonus", "isenção", "isencao", "facilidade", "black", "gratuito",
]


def _is_promo_related(text: str) -> bool:
    return any(kw in text.lower() for kw in _PROMO_KEYWORDS)


def promo_search_node(state: AgentState) -> AgentState:
    raw_promos: list[RawPromo] = []

    for card in state["discovered_cards"]:
        card_name = card["card_name"]
        query = f"{card_name} promoção aprovação anuidade 2026"

        brave_results = search_brave_for_promotions.invoke({"query": query})
        for r in brave_results:
            text = f"{r['title']} {r['description']}"
            if _is_promo_related(text):
                raw_promos.append(RawPromo(
                    card_name=card_name,
                    text=text[:300],
                    url=r["url"],
                    source_name=r["source_name"],
                ))

        reddit_results = search_reddit_for_black_cards.invoke({"query": query})
        for r in reddit_results:
            text = f"{r['title']} {r['text']}"
            if _is_promo_related(text):
                raw_promos.append(RawPromo(
                    card_name=card_name,
                    text=text[:300],
                    url=r["url"],
                    source_name=r["source_name"],
                ))

    hardmob_results = scrape_hardmob_for_black_cards.invoke({})
    for r in hardmob_results:
        raw_promos.append(RawPromo(
            card_name="Descoberta Hardmob",
            text=r["title"],
            url=r["url"],
            source_name="Hardmob",
        ))

    return {**state, "raw_promos": raw_promos}
