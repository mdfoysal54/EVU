from __future__ import annotations

from ..ir import DiagramIR, EdgeType, make_edge, make_node


def build(prompt: str, title: str | None = None) -> DiagramIR:
    diagram = DiagramIR(
        id="sequence",
        diagram_type="sequence",
        title=title or "Sequence Diagram",
        direction="LR",
    )

    participants = [
        ("user", "User"),
        ("client", "Client"),
        ("api", "API"),
        ("agent", "AI Agent"),
        ("database", "Database"),
    ]

    for node_id, label in participants:
        diagram.add_node(
            make_node(
                node_id,
                label,
                "participant",
            )
        )

    messages = [
        ("user", "client", "request"),
        ("client", "api", "HTTP request"),
        ("api", "agent", "process"),
        ("agent", "database", "query"),
        ("database", "agent", "result"),
        ("agent", "api", "response"),
        ("api", "client", "HTTP response"),
        ("client", "user", "display"),
    ]

    for source, target, label in messages:
        diagram.add_edge(
            make_edge(
                source,
                target,
                label,
                EdgeType.MESSAGE,
            )
        )

    return diagram