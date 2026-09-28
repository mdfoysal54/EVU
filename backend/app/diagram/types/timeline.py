from __future__ import annotations

from ..ir import DiagramIR, EdgeType, make_edge, make_node


def build(prompt: str, title: str | None = None) -> DiagramIR:
    diagram = DiagramIR(
        id="timeline",
        diagram_type="timeline",
        title=title or "Timeline",
        direction="LR",
    )

    events = [
        ("event_1", "Planning"),
        ("event_2", "Development"),
        ("event_3", "Testing"),
        ("event_4", "Deployment"),
        ("event_5", "Production"),
    ]

    for node_id, label in events:
        diagram.add_node(
            make_node(
                node_id,
                label,
                "event",
            )
        )

    for index in range(1, len(events)):
        diagram.add_edge(
            make_edge(
                events[index - 1][0],
                events[index][0],
                edge_type=EdgeType.FLOW,
            )
        )

    return diagram