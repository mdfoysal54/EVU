from __future__ import annotations

from ..ir import DiagramIR, EdgeType, make_edge, make_node


def build(prompt: str, title: str | None = None) -> DiagramIR:
    diagram = DiagramIR(
        id="dependency",
        diagram_type="dependency",
        title=title or "Dependency Graph",
        direction="LR",
    )

    modules = [
        ("frontend", "Frontend"),
        ("api", "API"),
        ("agent", "Agent"),
        ("memory", "Memory"),
        ("tools", "Tools"),
        ("database", "Database"),
    ]

    for node_id, label in modules:
        diagram.add_node(
            make_node(
                node_id,
                label,
                "module",
            )
        )

    dependencies = [
        ("frontend", "api"),
        ("api", "agent"),
        ("agent", "memory"),
        ("agent", "tools"),
        ("memory", "database"),
        ("tools", "database"),
    ]

    for source, target in dependencies:
        diagram.add_edge(
            make_edge(
                source,
                target,
                "depends on",
                EdgeType.DEPENDENCY,
            )
        )

    return diagram