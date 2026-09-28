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
    Build a generic database schema diagram.

    Metadata contains column information so future renderers can
    display proper ER/database tables.
    """

    diagram = DiagramIR(
        id="database",
        diagram_type="database",
        title=title or "Database Schema",
        direction="LR",
    )

    tables = {
        "users": [
            ("id", "UUID", "PK"),
            ("email", "VARCHAR", "UNIQUE"),
            ("created_at", "TIMESTAMP", ""),
        ],
        "accounts": [
            ("id", "UUID", "PK"),
            ("user_id", "UUID", "FK"),
            ("provider", "VARCHAR", ""),
        ],
        "conversations": [
            ("id", "UUID", "PK"),
            ("user_id", "UUID", "FK"),
            ("title", "VARCHAR", ""),
        ],
        "messages": [
            ("id", "UUID", "PK"),
            ("conversation_id", "UUID", "FK"),
            ("role", "VARCHAR", ""),
            ("content", "TEXT", ""),
        ],
    }

    for table_name, columns in tables.items():
        diagram.add_node(
            make_node(
                table_name,
                table_name.title(),
                "table",
                shape=NodeShape.CYLINDER,
                metadata={
                    "columns": [
                        {
                            "name": name,
                            "type": data_type,
                            "constraint": constraint,
                        }
                        for name, data_type, constraint in columns
                    ]
                },
            )
        )

    relationships = [
        ("users", "accounts", "1:N"),
        ("users", "conversations", "1:N"),
        ("conversations", "messages", "1:N"),
    ]

    for source, target, label in relationships:
        diagram.add_edge(
            make_edge(
                source,
                target,
                label,
                EdgeType.ASSOCIATION,
            )
        )

    return diagram