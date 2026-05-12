from ..state import AgentState, RawPromo
from ...tools.rss_tool import search_rss_for_black_cards
from ...tools.youtube_tool import search_youtube_for_black_cards
from ...tools.brave_tool import search_brave_for_promotions
from ...tools.scraper_tool import scrape_hardmob_for_black_cards

_PROMO_KEYWORDS = ["promoção", "promocao", "anuidade", "aprovado", "aprovação", "bônus", "bonus", "isenção", "isencao", "facilidade", "black", "gratuito"]


def _is_promo_related(text: str) -> bool:
    return any(kw in text.lower() for kw in _PROMO_KEYWORDS)


def _match_card(title: str, discovered_cards: list[dict]) -> str:
    """Return the discovered card name if found in the title, else a generic fallback."""
    title_lower = title.lower()
    for card in discovered_cards:
        card_words = card["card_name"].lower().split()
        if any(word in title_lower for word in card_words if len(word) > 3):
            return card["card_name"]
    return "Cartão Premium"


def promo_search_node(state: AgentState) -> AgentState:
    raw_promos: list[RawPromo] = []
    discovered = state["discovered_cards"]

    for card in discovered:
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

        rss_results = search_rss_for_black_cards.invoke({"query": query})
        for r in rss_results:
            text = f"{r['title']} {r['text']}"
            if _is_promo_related(text):
                raw_promos.append(RawPromo(
                    card_name=card_name,
                    text=text[:300],
                    url=r["url"],
                    source_name=r["source_name"],
                ))

        youtube_results = search_youtube_for_black_cards.invoke({"query": query})
        for r in youtube_results:
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
        matched_card = _match_card(r["title"], discovered)
        raw_promos.append(RawPromo(
            card_name=matched_card,
            text=r["title"],
            url=r["url"],
            source_name="Hardmob",
        ))

    return {**state, "raw_promos": raw_promos}
