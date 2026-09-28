from __future__ import annotations

from ..ir import DiagramIR, EdgeType, NodeShape, make_edge, make_node


def build(prompt: str, title: str | None = None) -> DiagramIR:
    diagram = DiagramIR(
        id="tree",
        diagram_type="tree",
        title=title or "Decision Tree",
        direction="TB",
    )

    nodes = [
        ("root", "Decision", NodeShape.DIAMOND),
        ("yes", "Yes", NodeShape.ROUNDED),
        ("no", "No", NodeShape.ROUNDED),
        ("yes_result", "Success", NodeShape.CIRCLE),
        ("no_result", "Retry", NodeShape.CIRCLE),
    ]

    for node_id, label, shape in nodes:
        diagram.add_node(
            make_node(
                node_id,
                label,
                "tree_node",
                shape=shape,
            )
        )

    edges = [
        ("root", "yes", "yes"),
        ("root", "no", "no"),
        ("yes", "yes_result", "complete"),
        ("no", "no_result", "retry"),
    ]

    for source, target, label in edges:
        diagram.add_edge(
            make_edge(
                source,
                target,
                label,
                EdgeType.FLOW,
            )
        )

    return diagram