from __future__ import annotations

import re

from ..ir import DiagramIR, EdgeType, NodeShape, make_edge, make_node


def _steps(prompt: str) -> list[str]:
    parts = re.split(
        r"\b(?:then|next|after that|followed by|->|→)\b|[,;]",
        prompt,
        flags=re.IGNORECASE,
    )

    cleaned = [
        part.strip(" .")
        for part in parts
        if part.strip(" .")
    ]

    return cleaned[:12] or ["Start", "Process", "End"]


def build(prompt: str, title: str | None = None) -> DiagramIR:
    steps = _steps(prompt)

    diagram = DiagramIR(
        id="flowchart",
        diagram_type="flowchart",
        title=title or "Flowchart",
        direction="TD",
    )

    for index, step in enumerate(steps):
        node_id = f"step_{index + 1}"

        shape = (
            NodeShape.CIRCLE
            if index == 0 or index == len(steps) - 1
            else NodeShape.ROUNDED
        )

        diagram.add_node(
            make_node(
                node_id,
                step,
                "step",
                shape=shape,
            )
        )

        if index:
            diagram.add_edge(
                make_edge(
                    f"step_{index}",
                    node_id,
                    edge_type=EdgeType.FLOW,
                )
            )

    return diagram