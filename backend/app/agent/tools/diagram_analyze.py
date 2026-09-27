from typing import Any, Dict
from app.diagram.budget import complexity_budget


def diagram_analyze_tool(diagram_ir_payload: Dict[str, Any]) -> Dict[str, Any]:
    """Inspects diagram complexity, metrics, and structural recommendations before rendering."""
    nodes = diagram_ir_payload.get("nodes", [])
    edges = diagram_ir_payload.get("edges", [])

    budget = complexity_budget(len(nodes), len(edges))

    # Detect isolated nodes
    connected_ids = {e.get("source") for e in edges} | {e.get("target") for e in edges}
    isolated_nodes = [n.get("id") for n in nodes if n.get("id") not in connected_ids]

    return {
        "status": "success",
        "node_count": len(nodes),
        "edge_count": len(edges),
        "complexity_level": budget["level"],
        "recommended_action": budget.get("recommended_action", "single_canvas"),
        "isolated_nodes": isolated_nodes,
        "is_budget_exceeded": budget["level"] == "split",
    }