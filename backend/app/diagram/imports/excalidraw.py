from __future__ import annotations

import json
from typing import Any

from ..ir import (
    DiagramIR,
    EdgeType,
    make_edge,
    make_node,
)


class ExcalidrawImporter:
    name = "excalidraw"

    def parse(
        self,
        source: str | dict[str, Any],
        *,
        title: str | None = None,
    ) -> DiagramIR:

        if isinstance(source, str):
            try:
                document = json.loads(source)
            except json.JSONDecodeError as exc:
                raise ValueError(
                    "Invalid Excalidraw JSON."
                ) from exc
        else:
            document = source

        diagram = DiagramIR(
            id="imported_excalidraw",
            diagram_type="flowchart",
            title=title or "Imported Excalidraw Diagram",
        )

        elements = document.get(
            "elements",
            [],
        )

        element_ids: set[str] = set()

        for element in elements:
            if element.get("isDeleted"):
                continue

            element_id = element.get("id")

            if not element_id:
                continue

            element_ids.add(element_id)

            text = element.get(
                "text"
            ) or element.get(
                "originalText"
            ) or element_id

            diagram.add_node(
                make_node(
                    element_id,
                    str(text),
                    "imported",
                    metadata={
                        "x": element.get("x"),
                        "y": element.get("y"),
                        "width": element.get("width"),
                        "height": element.get("height"),
                    },
                )
            )

        for element in elements:
            if element.get("isDeleted"):
                continue

            start_binding = element.get(
                "startBinding"
            )
            end_binding = element.get(
                "endBinding"
            )

            if not start_binding or not end_binding:
                continue

            source_id = start_binding.get(
                "elementId"
            )
            target_id = end_binding.get(
                "elementId"
            )

            if (
                source_id in element_ids
                and target_id in element_ids
            ):
                diagram.add_edge(
                    make_edge(
                        source_id,
                        target_id,
                        edge_type=EdgeType.FLOW,
                    )
                )

        return diagram


def parse_excalidraw(
    source: str | dict[str, Any],
    title: str | None = None,
) -> DiagramIR:
    return ExcalidrawImporter().parse(
        source,
        title=title,
    )