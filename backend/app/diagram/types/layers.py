from __future__ import annotations

from ..ir import DiagramGroup, DiagramIR, EdgeType, make_edge, make_node


def build(prompt: str, title: str | None = None) -> DiagramIR:
    diagram = DiagramIR(
        id="layers",
        diagram_type="layers",
        title=title or "Layered Architecture",
        direction="TB",
    )

    layers = [
        ("presentation", "Presentation Layer"),
        ("application", "Application Layer"),
        ("domain", "Domain Layer"),
        ("data", "Data Layer"),
    ]

    for group_id, label in layers:
        diagram.add_group(
            DiagramGroup(
                id=group_id,
                label=label,
                group_type="layer",
            )
        )

    layer_nodes = [
        ("ui", "Web UI", "presentation"),
        ("api", "API", "application"),
        ("services", "Services", "application"),
        ("business", "Business Logic", "domain"),
        ("repository", "Repository", "data"),
        ("database", "Database", "data"),
    ]

    for node_id, label, group_id in layer_nodes:
        diagram.add_node(
            make_node(
                node_id,
                label,
                "component",
                group_id=group_id,
            )
        )

    edges = [
        ("ui", "api"),
        ("api", "services"),
        ("services", "business"),
        ("business", "repository"),
        ("repository", "database"),
    ]

    for source, target in edges:
        diagram.add_edge(
            make_edge(
                source,
                target,
                edge_type=EdgeType.DEPENDENCY,
            )
        )

    return diagram