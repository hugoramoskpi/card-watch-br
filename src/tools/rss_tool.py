import feedparser
from langchain_core.tools import tool

_RSS_FEEDS = [
    "https://www.infomoney.com.br/feed/",
    "https://culturadocredito.com.br/feed/",
    "https://www.meucartaodecredito.com.br/feed/",
    "https://blog.nubank.com.br/feed/",
    "https://blog.c6bank.com.br/feed/",
]

_BLACK_KEYWORDS = [
    "black", "premium", "infinite", "ultravioleta", "carbon", "platinum",
    "promoção", "anuidade", "aprovação", "bônus", "isenção",
]


@tool
def search_rss_for_black_cards(query: str) -> list[dict]:
    """Search Brazilian financial RSS feeds for premium/black card mentions.

    Args:
        query: search terms (e.g. 'inter black anuidade')

    Returns:
        List of dicts with keys: title, text, url, source_name
    """
    query_words = [w for w in query.lower().split() if len(w) > 3]
    results = []

    for feed_url in _RSS_FEEDS:
        try:
            feed = feedparser.parse(feed_url, agent="CardWatchBR/1.0")
            source_name = feed.feed.get("title", feed_url)
            for entry in feed.entries[:30]:
                title = entry.get("title", "")
                summary = entry.get("summary", "")
                text = f"{title} {summary}".lower()
                if any(w in text for w in query_words) or any(kw in text for kw in _BLACK_KEYWORDS):
                    results.append({
                        "title": title,
                        "text": summary[:500],
                        "url": entry.get("link", feed_url),
                        "source_name": f"RSS: {source_name}",
                    })
        except Exception:
            continue

    return results
