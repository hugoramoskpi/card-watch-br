from src.agent.state import AgentState
from src.agent.graph import build_graph


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
