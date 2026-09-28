from __future__ import annotations

from ..ir import (
    DiagramIR,
    EdgeType,
    NodeShape,
    make_edge,
    make_node,
)


def build(
    prompt: str,
    title: str | None = None,
) -> DiagramIR:
    """
    Build a generic UML-style class diagram.

    This is intentionally deterministic. Later the EVU AI engine
    can populate actual classes/methods/relationships from the prompt.
    """

    diagram = DiagramIR(
        id="uml",
        diagram_type="uml",
        title=title or "UML Class Diagram",
        direction="LR",
    )

    classes = [
        ("user", "User"),
        ("account", "Account"),
        ("conversation", "Conversation"),
        ("message", "Message"),
    ]

    for node_id, label in classes:
        diagram.add_node(
            make_node(
                node_id,
                label,
                "class",
                shape=NodeShape.RECTANGLE,
                metadata={
                    "uml": {
                        "attributes": [],
                        "methods": [],
                    }
                },
            )
        )

    relationships = [
        ("user", "account", "owns", EdgeType.ASSOCIATION),
        ("user", "conversation", "creates", EdgeType.ASSOCIATION),
        ("conversation", "message", "contains", EdgeType.COMPOSITION),
        ("user", "message", "sends", EdgeType.ASSOCIATION),
    ]

    for source, target, label, edge_type in relationships:
        diagram.add_edge(
            make_edge(
                source,
                target,
                label,
                edge_type,
            )
        )

    return diagram