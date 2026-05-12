from unittest.mock import MagicMock, patch
from src.tools.reddit_tool import search_reddit_for_black_cards

def test_reddit_tool_returns_list():
    mock_submission = MagicMock()
    mock_submission.title = "Inter Black com anuidade zero aprovado!"
    mock_submission.selftext = "Consegui o Inter Black com renda de 5k"
    mock_submission.permalink = "/r/investimentos/comments/abc123"
    mock_submission.score = 42

    with patch("src.tools.reddit_tool.praw.Reddit") as MockReddit:
        mock_reddit = MockReddit.return_value
        mock_reddit.subreddit.return_value.search.return_value = [mock_submission]
        results = search_reddit_for_black_cards.invoke({"query": "inter black"})

    assert isinstance(results, list)
    assert len(results) > 0
    assert results[0]["title"] == "Inter Black com anuidade zero aprovado!"
    assert "reddit.com" in results[0]["url"]
    assert results[0]["source_name"].startswith("Reddit r/")


from unittest.mock import patch
from src.tools.brave_tool import search_brave_for_promotions

def test_brave_tool_returns_list():
    mock_response = {
        "web": {
            "results": [
                {
                    "title": "C6 Carbon aprova com 15k de renda",
                    "description": "Promoção especial até junho...",
                    "url": "https://hardmob.com.br/thread/123",
                }
            ]
        }
    }
    with patch("src.tools.brave_tool.requests.get") as mock_get:
        mock_get.return_value.json.return_value = mock_response
        mock_get.return_value.raise_for_status = lambda: None
        results = search_brave_for_promotions.invoke({"query": "C6 Carbon promoção"})

    assert len(results) == 1
    assert results[0]["title"] == "C6 Carbon aprova com 15k de renda"
    assert results[0]["source_name"] == "Brave Search"


from unittest.mock import MagicMock, patch
from src.tools.scraper_tool import scrape_hardmob_for_black_cards

def test_scraper_returns_list_on_success():
    mock_thread = MagicMock()
    mock_thread.inner_text.return_value = "Inter Black aprovado com facilidade"
    mock_thread.get_attribute.return_value = "https://hardmob.com.br/thread/456"

    with patch("src.tools.scraper_tool.sync_playwright") as mock_pw:
        mock_browser = MagicMock()
        mock_page = MagicMock()
        mock_page.query_selector_all.return_value = [mock_thread]
        mock_browser.new_page.return_value = mock_page
        mock_pw.return_value.__enter__.return_value.chromium.launch.return_value = mock_browser
        results = scrape_hardmob_for_black_cards.invoke({})

    assert isinstance(results, list)

def test_scraper_returns_empty_list_on_error():
    with patch("src.tools.scraper_tool.sync_playwright") as mock_pw:
        mock_pw.return_value.__enter__.return_value.chromium.launch.side_effect = Exception("network error")
        results = scrape_hardmob_for_black_cards.invoke({})
    assert results == []
