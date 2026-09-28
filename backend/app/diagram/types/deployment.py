from __future__ import annotations

from ..ir import DiagramGroup, DiagramIR, EdgeType, NodeShape, make_edge, make_node


def build(prompt: str, title: str | None = None) -> DiagramIR:
    diagram = DiagramIR(
        id="deployment",
        diagram_type="deployment",
        title=title or "Deployment Diagram",
        direction="LR",
    )

    diagram.add_group(
        DiagramGroup(
            id="cloud",
            label="Cloud Environment",
            group_type="environment",
        )
    )

    diagram.add_group(
        DiagramGroup(
            id="app",
            label="Application",
            group_type="environment",
            parent_id="cloud",
        )
    )

    nodes = [
        make_node(
            "load_balancer",
            "Load Balancer",
            "infrastructure",
            shape=NodeShape.HEXAGON,
        ),
        make_node(
            "api",
            "API Server",
            "container",
            group_id="app",
        ),
        make_node(
            "worker",
            "Worker",
            "container",
            group_id="app",
        ),
        make_node(
            "database",
            "Database",
            "database",
            group_id="cloud",
            shape=NodeShape.CYLINDER,
        ),
        make_node(
            "cache",
            "Redis",
            "cache",
            group_id="cloud",
            shape=NodeShape.CYLINDER,
        ),
    ]

    for node in nodes:
        diagram.add_node(node)

    edges = [
        ("load_balancer", "api", "HTTP"),
        ("api", "worker", "jobs"),
        ("api", "database", "SQL"),
        ("api", "cache", "cache"),
        ("worker", "database", "SQL"),
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