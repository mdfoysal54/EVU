from __future__ import annotations

import re
import xml.etree.ElementTree as ET

from ..ir import (
    DiagramIR,
    EdgeType,
    make_edge,
    make_node,
)


class DrawioImporter:
    name = "drawio"

    def parse(
        self,
        source: str,
        *,
        title: str | None = None,
    ) -> DiagramIR:

        diagram = DiagramIR(
            id="imported_drawio",
            diagram_type="architecture",
            title=title or "Imported Draw.io Diagram",
        )

        try:
            root = ET.fromstring(source)
        except ET.ParseError as exc:
            raise ValueError(
                "Invalid Draw.io XML."
            ) from exc

        for cell in root.iter():
            if cell.tag.endswith("mxCell"):
                cell_id = cell.attrib.get("id")

                if not cell_id:
                    continue

                value = cell.attrib.get(
                    "value",
                    "",
                )

                source_id = cell.attrib.get(
                    "source"
                )
                target_id = cell.attrib.get(
                    "target"
                )

                if source_id and target_id:
                    if not diagram.get_node(source_id):
                        diagram.add_node(
                            make_node(
                                source_id,
                                source_id,
                                "imported",
                            )
                        )

                    if not diagram.get_node(target_id):
                        diagram.add_node(
                            make_node(
                                target_id,
                                target_id,
                                "imported",
                            )
                        )

                    label = re.sub(
                        r"<[^>]+>",
                        "",
                        value,
                    ).strip()

                    diagram.add_edge(
                        make_edge(
                            source_id,
                            target_id,
                            label or None,
                            EdgeType.FLOW,
                        )
                    )

                elif value:
                    label = re.sub(
                        r"<[^>]+>",
                        "",
                        value,
                    ).strip()

                    diagram.add_node(
                        make_node(
                            cell_id,
                            label or cell_id,
                            "imported",
                        )
                    )

        return diagram


def parse_drawio(
    source: str,
    title: str | None = None,
) -> DiagramIR:
    return DrawioImporter().parse(
        source,
        title=title,
    )