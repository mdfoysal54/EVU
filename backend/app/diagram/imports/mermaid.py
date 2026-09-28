from __future__ import annotations

import re

from ..ir import (
    DiagramIR,
    EdgeType,
    make_edge,
    make_node,
)


NODE_PATTERN = re.compile(
    r'^\s*([A-Za-z_][\w-]*)\s*'
    r'\["([^"]+)"\]\s*$'
)

EDGE_PATTERN = re.compile(
    r'^\s*([A-Za-z_][\w-]*)\s*'
    r'(?:-->|---|-.->|==>)'
    r'\s*(?:\|"?([^"|]+)"?\|)?\s*'
    r'([A-Za-z_][\w-]*)'
)


class MermaidImporter:
    name = "mermaid"

    def parse(
        self,
        source: str,
        *,
        title: str | None = None,
    ) -> DiagramIR:

        lines = source.splitlines()

        direction = "TD"

        diagram = DiagramIR(
            id="imported_mermaid",
            diagram_type="flowchart",
            title=title or "Imported Mermaid Diagram",
            direction=direction,
        )

        for raw_line in lines:
            line = raw_line.strip()

            if not line:
                continue

            if line.startswith("flowchart"):
                parts = line.split()

                if len(parts) > 1:
                    direction = parts[1]

                diagram.direction = direction
                continue

            node_match = NODE_PATTERN.match(line)

            if node_match:
                node_id, label = node_match.groups()

                diagram.add_node(
                    make_node(
                        node_id,
                        label,
                        "imported",
                    )
                )

                continue

            edge_match = EDGE_PATTERN.match(line)

            if edge_match:
                source_id, label, target_id = (
                    edge_match.groups()
                )

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

                diagram.add_edge(
                    make_edge(
                        source_id,
                        target_id,
                        label,
                        EdgeType.FLOW,
                    )
                )

        return diagram


def parse_mermaid(
    source: str,
    title: str | None = None,
) -> DiagramIR:
    return MermaidImporter().parse(
        source,
        title=title,
    )