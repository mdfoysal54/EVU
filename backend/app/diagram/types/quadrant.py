from __future__ import annotations

from ..ir import DiagramIR, make_node


def build(prompt: str, title: str | None = None) -> DiagramIR:
    diagram = DiagramIR(
        id="quadrant",
        diagram_type="quadrant",
        title=title or "Quadrant Matrix",
        direction="TB",
    )

    quadrants = [
        ("top_left", "High Priority / Low Effort"),
        ("top_right", "High Priority / High Effort"),
        ("bottom_left", "Low Priority / Low Effort"),
        ("bottom_right", "Low Priority / High Effort"),
    ]

    for node_id, label in quadrants:
        diagram.add_node(
            make_node(
                node_id,
                label,
                "quadrant",
            )
        )

    return diagram