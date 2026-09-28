from __future__ import annotations

from ..ir import DiagramIR, EdgeType, make_edge, make_node


def build(prompt: str, title: str | None = None) -> DiagramIR:
    diagram = DiagramIR(
        id="hierarchy",
        diagram_type="hierarchy",
        title=title or "Hierarchy",
        direction="TB",
    )

    nodes = [
        ("ceo", "CEO"),
        ("cto", "CTO"),
        ("cpo", "Product"),
        ("engineering", "Engineering"),
        ("design", "Design"),
        ("qa", "QA"),
    ]

    for node_id, label in nodes:
        diagram.add_node(
            make_node(
                node_id,
                label,
                "role",
            )
        )

    edges = [
        ("ceo", "cto"),
        ("ceo", "cpo"),
        ("cto", "engineering"),
        ("cpo", "design"),
        ("engineering", "qa"),
    ]

    for source, target in edges:
        diagram.add_edge(
            make_edge(
                source,
                target,
                edge_type=EdgeType.ASSOCIATION,
            )
        )

    return diagram