from unittest.mock import patch, MagicMock

from src.agent.state import AgentState
from src.agent.graph import build_graph
from src.agent.nodes.discovery import discovery_node


def test_graph_compiles():
    graph = build_graph()
    assert graph is not None


def test_initial_state_structure():
    state: AgentState = {
        "cycle_id": "test-cycle",
        "discovered_cards": [],
        "raw_promos": [],
        "validated_promos": [],
        "alerts_sent": [],
    }
    assert state["cycle_id"] == "test-cycle"
    assert state["discovered_cards"] == []


def _base_state() -> AgentState:
    return {
        "cycle_id": "",
        "discovered_cards": [],
        "raw_promos": [],
        "validated_promos": [],
        "alerts_sent": [],
    }


def test_discovery_node_populates_discovered_cards():
    mock_reddit_results = [{"title": "Inter Black aprovado", "text": "", "url": "https://reddit.com/1", "score": 10, "source_name": "Reddit r/investimentos"}]
    mock_brave_results = [{"title": "C6 Carbon promoção", "description": "Aprovação fácil", "url": "https://hardmob.com/1", "source_name": "Brave Search"}]

    mock_llm_response = MagicMock()
    mock_llm_response.content = '{"cards": [{"card_name": "Inter Black", "buzz_score": 8, "mentions_count": 2, "sources": ["Reddit r/investimentos", "Brave Search"]}]}'

    with patch("src.agent.nodes.discovery.search_reddit_for_black_cards") as mock_reddit, \
         patch("src.agent.nodes.discovery.search_brave_for_promotions") as mock_brave, \
         patch("src.agent.nodes.discovery.ChatAnthropic") as MockLLM:

        mock_reddit.invoke.return_value = mock_reddit_results
        mock_brave.invoke.return_value = mock_brave_results
        MockLLM.return_value.invoke.return_value = mock_llm_response

        result = discovery_node(_base_state())

    assert len(result["discovered_cards"]) == 1
    assert result["discovered_cards"][0]["card_name"] == "Inter Black"
    assert result["cycle_id"] != ""


# ── Task 8: PromoSearch ────────────────────────────────────────────────────────

from src.agent.nodes.promo_search import promo_search_node

def test_promo_search_node_populates_raw_promos():
    state = {**_base_state(), "discovered_cards": [
        {"card_name": "Inter Black", "buzz_score": 8, "mentions_count": 2, "sources": ["Reddit"]}
    ]}
    mock_brave = [{"title": "Inter Black anuidade zero", "description": "Promoção válida por 12 meses", "url": "https://example.com", "source_name": "Brave Search"}]

    with patch("src.agent.nodes.promo_search.search_brave_for_promotions") as mock_b, \
         patch("src.agent.nodes.promo_search.search_reddit_for_black_cards") as mock_r, \
         patch("src.agent.nodes.promo_search.scrape_hardmob_for_black_cards") as mock_s:
        mock_b.invoke.return_value = mock_brave
        mock_r.invoke.return_value = []
        mock_s.invoke.return_value = []
        result = promo_search_node(state)

    assert len(result["raw_promos"]) > 0
    assert result["raw_promos"][0]["card_name"] == "Inter Black"
