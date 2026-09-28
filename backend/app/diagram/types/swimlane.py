from __future__ import annotations

from ..ir import DiagramGroup, DiagramIR, EdgeType, make_edge, make_node


def build(prompt: str, title: str | None = None) -> DiagramIR:
    diagram = DiagramIR(
        id="swimlane",
        diagram_type="swimlane",
        title=title or "Swimlane Diagram",
        direction="LR",
    )

    lanes = [
        ("user_lane", "User"),
        ("frontend_lane", "Frontend"),
        ("backend_lane", "Backend"),
        ("database_lane", "Database"),
    ]

    for lane_id, label in lanes:
        diagram.add_group(
            DiagramGroup(
                id=lane_id,
                label=label,
                group_type="swimlane",
            )
        )

    actions = [
        ("request", "Send Request", "user_lane"),
        ("ui", "Submit Request", "frontend_lane"),
        ("api", "Process Request", "backend_lane"),
        ("db", "Read Data", "database_lane"),
        ("response", "Return Result", "backend_lane"),
        ("display", "Display Result", "frontend_lane"),
    ]

    for node_id, label, group_id in actions:
        diagram.add_node(
            make_node(
                node_id,
                label,
                "action",
                group_id=group_id,
            )
        )

    connections = [
        ("request", "ui"),
        ("ui", "api"),
        ("api", "db"),
        ("db", "response"),
        ("response", "display"),
    ]

    for source, target in connections:
        diagram.add_edge(
            make_edge(
                source,
                target,
                edge_type=EdgeType.FLOW,
            )
        )

    return diagram