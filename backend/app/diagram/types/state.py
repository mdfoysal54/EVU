from __future__ import annotations

from ..ir import DiagramIR, EdgeType, NodeShape, make_edge, make_node


def build(prompt: str, title: str | None = None) -> DiagramIR:
    diagram = DiagramIR(
        id="state",
        diagram_type="state",
        title=title or "State Diagram",
        direction="LR",
    )

    states = [
        ("idle", "Idle"),
        ("processing", "Processing"),
        ("success", "Success"),
        ("failed", "Failed"),
    ]

    for node_id, label in states:
        diagram.add_node(
            make_node(
                node_id,
                label,
                "state",
                shape=NodeShape.ROUNDED,
            )
        )

    transitions = [
        ("idle", "processing", "start"),
        ("processing", "success", "complete"),
        ("processing", "failed", "error"),
        ("failed", "processing", "retry"),
        ("success", "idle", "reset"),
    ]

    for source, target, label in transitions:
        diagram.add_edge(
            make_edge(
                source,
                target,
                label,
                EdgeType.TRANSITION,
            )
        )

    return diagram