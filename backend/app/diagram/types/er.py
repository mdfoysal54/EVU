from __future__ import annotations

from ..ir import DiagramIR, EdgeType, NodeShape, make_edge, make_node


def build(prompt: str, title: str | None = None) -> DiagramIR:
    diagram = DiagramIR(
        id="er",
        diagram_type="er",
        title=title or "Entity Relationship Diagram",
        direction="LR",
    )

    entities = [
        ("users", "Users"),
        ("accounts", "Accounts"),
        ("conversations", "Conversations"),
        ("messages", "Messages"),
    ]

    for node_id, label in entities:
        diagram.add_node(
            make_node(
                node_id,
                label,
                "entity",
                shape=NodeShape.RECTANGLE,
            )
        )

    relationships = [
        ("users", "accounts", "owns"),
        ("users", "conversations", "creates"),
        ("conversations", "messages", "contains"),
        ("users", "messages", "sends"),
    ]

    for source, target, label in relationships:
        diagram.add_edge(
            make_edge(
                source,
                target,
                label,
                EdgeType.ASSOCIATION,
                directed=True,
            )
        )

    return diagram