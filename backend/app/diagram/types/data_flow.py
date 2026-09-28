from __future__ import annotations

from ..ir import DiagramIR, EdgeType, NodeShape, make_edge, make_node


def build(prompt: str, title: str | None = None) -> DiagramIR:
    diagram = DiagramIR(
        id="data_flow",
        diagram_type="data_flow",
        title=title or "Data Flow",
        direction="LR",
    )

    nodes = [
        ("source", "Data Source", NodeShape.CYLINDER),
        ("ingestion", "Ingestion", NodeShape.ROUNDED),
        ("processing", "Processing", NodeShape.ROUNDED),
        ("storage", "Data Store", NodeShape.CYLINDER),
        ("analytics", "Analytics", NodeShape.ROUNDED),
        ("consumer", "Consumer", NodeShape.ROUNDED),
    ]

    for node_id, label, shape in nodes:
        diagram.add_node(
            make_node(
                node_id,
                label,
                "data_component",
                shape=shape,
            )
        )

    for index in range(1, len(nodes)):
        diagram.add_edge(
            make_edge(
                nodes[index - 1][0],
                nodes[index][0],
                "data",
                EdgeType.DATA,
            )
        )

    return diagram