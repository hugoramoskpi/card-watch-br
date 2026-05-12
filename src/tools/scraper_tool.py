from playwright.sync_api import sync_playwright
from langchain_core.tools import tool

_BLACK_KEYWORDS = ["black", "premium", "infinite", "ultravioleta", "carbon", "platinum"]
_HARDMOB_URL = "https://www.hardmob.com.br/forums/295-Cartoes-de-Credito"

@tool
def scrape_hardmob_for_black_cards() -> list[dict]:
    """Scrape Hardmob credit card forum for recent black/premium card threads.

    Returns:
        List of dicts with keys: title, url, source_name
    """
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto(_HARDMOB_URL, timeout=15000)
            page.wait_for_selector("h3.threadtitle", timeout=5000)
            threads = page.query_selector_all("h3.threadtitle a")
            results = []
            for thread in threads[:20]:
                title = thread.inner_text()
                if any(kw in title.lower() for kw in _BLACK_KEYWORDS):
                    results.append({
                        "title": title,
                        "url": thread.get_attribute("href") or _HARDMOB_URL,
                        "source_name": "Hardmob",
                    })
            browser.close()
            return results
    except Exception:
        return []
