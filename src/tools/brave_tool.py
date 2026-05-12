import os
import requests
from langchain_core.tools import tool

_BRAVE_URL = "https://api.search.brave.com/res/v1/web/search"

@tool
def search_brave_for_promotions(query: str) -> list[dict]:
    """Search the web via Brave Search API for premium card promotions.

    Args:
        query: search terms (e.g. 'cartão black promoção anuidade')

    Returns:
        List of dicts with keys: title, description, url, source_name
    """
    headers = {
        "Accept": "application/json",
        "Accept-Encoding": "gzip",
        "X-Subscription-Token": os.environ.get("BRAVE_SEARCH_API_KEY", ""),
    }
    params = {"q": query, "count": 10, "freshness": "pw"}
    response = requests.get(_BRAVE_URL, headers=headers, params=params, timeout=10)
    response.raise_for_status()
    data = response.json()
    return [
        {
            "title": item.get("title", ""),
            "description": item.get("description", ""),
            "url": item.get("url", ""),
            "source_name": "Brave Search",
        }
        for item in data.get("web", {}).get("results", [])
    ]
