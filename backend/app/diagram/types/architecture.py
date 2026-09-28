from __future__ import annotations

from ..ir import DiagramIR, DiagramGroup, EdgeType, NodeShape, make_edge, make_node


def build(prompt: str, title: str | None = None) -> DiagramIR:
    diagram = DiagramIR(
        id="architecture",
        diagram_type="architecture",
        title=title or "System Architecture",
        direction="LR",
    )

    diagram.add_group(
        DiagramGroup(
            id="client_layer",
            label="Client",
            group_type="layer",
        )
    )

    diagram.add_group(
        DiagramGroup(
            id="backend_layer",
            label="Backend",
            group_type="layer",
        )
    )

    diagram.add_group(
        DiagramGroup(
            id="data_layer",
            label="Data",
            group_type="layer",
        )
    )

    nodes = [
        make_node(
            "client",
            "Web / Mobile Client",
            "client",
            group_id="client_layer",
            shape=NodeShape.ROUNDED,
        ),
        make_node(
            "api",
            "API Gateway",
            "gateway",
            group_id="backend_layer",
            shape=NodeShape.HEXAGON,
        ),
        make_node(
            "agent",
            "AI Agent",
            "agent",
            group_id="backend_layer",
        ),
        make_node(
            "database",
            "Database",
            "database",
            group_id="data_layer",
            shape=NodeShape.CYLINDER,
        ),
        make_node(
            "cache",
            "Cache",
            "cache",
            group_id="data_layer",
            shape=NodeShape.CYLINDER,
        ),
    ]

    for node in nodes:
        diagram.add_node(node)

    diagram.add_edge(
        make_edge("client", "api", "HTTP", EdgeType.FLOW)
    )
    diagram.add_edge(
        make_edge("api", "agent", "request", EdgeType.FLOW)
    )
    diagram.add_edge(
        make_edge("agent", "database", "read/write", EdgeType.DATA)
    )
    diagram.add_edge(
        make_edge("agent", "cache", "cache", EdgeType.DATA)
    )

    return diagram