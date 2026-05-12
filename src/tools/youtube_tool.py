import os
import requests
from langchain_core.tools import tool

_YOUTUBE_SEARCH_URL = "https://www.googleapis.com/youtube/v3/search"


@tool
def search_youtube_for_black_cards(query: str) -> list[dict]:
    """Search YouTube for Brazilian videos about premium/black credit card promotions.

    Args:
        query: search terms (e.g. 'cartão black promoção 2026')

    Returns:
        List of dicts with keys: title, text, url, source_name
    """
    api_key = os.environ.get("YOUTUBE_API_KEY", "")
    if not api_key:
        return []

    try:
        params = {
            "part": "snippet",
            "q": query,
            "type": "video",
            "regionCode": "BR",
            "relevanceLanguage": "pt",
            "order": "date",
            "maxResults": 10,
            "key": api_key,
        }
        response = requests.get(_YOUTUBE_SEARCH_URL, params=params, timeout=10)
        response.raise_for_status()
        items = response.json().get("items", [])

        results = []
        for item in items:
            snippet = item.get("snippet", {})
            video_id = item.get("id", {}).get("videoId", "")
            results.append({
                "title": snippet.get("title", ""),
                "text": snippet.get("description", "")[:500],
                "url": f"https://www.youtube.com/watch?v={video_id}",
                "source_name": f"YouTube: {snippet.get('channelTitle', 'Canal')}",
            })
        return results
    except Exception:
        return []
