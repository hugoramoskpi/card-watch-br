from langgraph.graph import StateGraph, END
from .state import AgentState
from .nodes.discovery import discovery_node
from .nodes.promo_search import promo_search_node
from .nodes.cross_validate import cross_validate_node
from .nodes.persist_alert import persist_alert_node


def build_graph():
    graph = StateGraph(AgentState)
    graph.add_node("discovery", discovery_node)
    graph.add_node("promo_search", promo_search_node)
    graph.add_node("cross_validate", cross_validate_node)
    graph.add_node("persist_alert", persist_alert_node)

    graph.set_entry_point("discovery")
    graph.add_edge("discovery", "promo_search")
    graph.add_edge("promo_search", "cross_validate")
    graph.add_edge("cross_validate", "persist_alert")
    graph.add_edge("persist_alert", END)

    return graph.compile()
