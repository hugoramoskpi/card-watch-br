import os
import praw
from langchain_core.tools import tool

_SUBREDDITS = ["investimentos", "financaspessoais", "brasil", "creditcard"]

def _get_reddit() -> praw.Reddit:
    return praw.Reddit(
        client_id=os.getenv("REDDIT_CLIENT_ID", ""),
        client_secret=os.getenv("REDDIT_CLIENT_SECRET", ""),
        user_agent=os.getenv("REDDIT_USER_AGENT", "CardWatchBR/1.0"),
    )

@tool
def search_reddit_for_black_cards(query: str) -> list[dict]:
    """Search Reddit for discussions about premium/black credit cards.

    Args:
        query: search terms (e.g. 'inter black anuidade')

    Returns:
        List of dicts with keys: title, text, url, score, source_name
    """
    reddit = _get_reddit()
    results = []
    for sub in _SUBREDDITS:
        for post in reddit.subreddit(sub).search(query, limit=10, sort="new", time_filter="day"):
            results.append({
                "title": post.title,
                "text": post.selftext[:500],
                "url": f"https://reddit.com{post.permalink}",
                "score": post.score,
                "source_name": f"Reddit r/{sub}",
            })
    return results
