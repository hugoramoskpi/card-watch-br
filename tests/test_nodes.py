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


# ── Task 9: CrossValidate ─────────────────────────────────────────────────────

from src.agent.nodes.cross_validate import cross_validate_node

def test_cross_validate_requires_min_sources():
    state = {**_base_state(), "raw_promos": [
        {"card_name": "BTG Black", "text": "50k bônus na adesão", "url": "https://reddit.com/1", "source_name": "Reddit r/investimentos"},
        {"card_name": "BTG Black", "text": "50k bônus na adesão de BTG", "url": "https://hardmob.com/1", "source_name": "Hardmob"},
        {"card_name": "Cartão X Desconhecido", "text": "oferta especial", "url": "https://spam.com", "source_name": "Brave Search"},
    ]}

    mock_response = MagicMock()
    mock_response.content = '[{"card_name": "BTG Black", "summary": "Bônus de 50k pontos na adesão ao BTG Black", "confidence": 2, "urls": ["https://reddit.com/1", "https://hardmob.com/1"], "sources": ["Reddit r/investimentos", "Hardmob"]}]'

    with patch("src.agent.nodes.cross_validate.ChatAnthropic") as MockLLM:
        MockLLM.return_value.invoke.return_value = mock_response
        result = cross_validate_node(state)

    assert len(result["validated_promos"]) == 1
    assert result["validated_promos"][0]["card_name"] == "BTG Black"
    assert result["validated_promos"][0]["confidence"] >= 2

def test_cross_validate_empty_when_no_promos():
    result = cross_validate_node(_base_state())
    assert result["validated_promos"] == []


# ── Task 10: Persist & Alert ──────────────────────────────────────────────────

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.db.models import Base
from src.agent.nodes.persist_alert import persist_alert_node

def test_persist_alert_saves_new_promos_to_db():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    db = Session()

    state = {**_base_state(), "validated_promos": [
        {"card_name": "Nubank Ultra", "summary": "Cashback 5% por 3 meses", "confidence": 2,
         "urls": ["https://reddit.com/1", "https://hardmob.com/1"], "sources": ["Reddit", "Hardmob"]}
    ]}

    with patch("src.agent.nodes.persist_alert.SessionLocal", return_value=db), \
         patch("src.agent.nodes.persist_alert._send_telegram_alert") as mock_tg:
        result = persist_alert_node(state)

    assert len(result["alerts_sent"]) == 1
    mock_tg.assert_called_once()
