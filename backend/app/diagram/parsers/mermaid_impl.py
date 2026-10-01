from __future__ import annotations

import re
from typing import Dict, List, Tuple

from ..ir.diagram import DiagramIR
from ..ir.nodes import IRNode
from ..ir.edges import IREdge


class MermaidParser:
    """
    Lightweight Mermaid parser.

    Supported diagrams:

    - flowchart
    - graph
    - sequenceDiagram
    - stateDiagram
    - classDiagram
    - erDiagram

    This parser intentionally handles the common Mermaid subset
    without requiring Node.js or Mermaid CLI.
    """

    def parse(
        self,
        source: str,
    ) -> DiagramIR:
        if not source or not source.strip():
            raise ValueError(
                "Mermaid source cannot be empty"
            )

        lines = [
            line.strip()
            for line in source.splitlines()
            if line.strip()
        ]

        if not lines:
            raise ValueError(
                "Mermaid source contains no content"
            )

        diagram_type = self._detect_type(
            lines
        )

        diagram = DiagramIR()

        if diagram_type in {
            "flowchart",
            "graph",
        }:
            self._parse_flowchart(
                diagram,
                lines,
            )

        elif diagram_type == "sequence":
            self._parse_sequence(
                diagram,
                lines,
            )

        elif diagram_type == "state":
            self._parse_state(
                diagram,
                lines,
            )

        elif diagram_type == "class":
            self._parse_class(
                diagram,
                lines,
            )

        elif diagram_type == "er":
            self._parse_er(
                diagram,
                lines,
            )

        else:
            raise ValueError(
                f"Unsupported Mermaid diagram type: {diagram_type}"
            )

        return diagram

    def _detect_type(
        self,
        lines: List[str],
    ) -> str:
        first = lines[0].lower()

        if first.startswith(
            "flowchart"
        ):
            return "flowchart"

        if first.startswith(
            "graph"
        ):
            return "graph"

        if first.startswith(
            "sequencediagram"
        ):
            return "sequence"

        if first.startswith(
            "statediagram"
        ):
            return "state"

        if first.startswith(
            "classdiagram"
        ):
            return "class"

        if first.startswith(
            "erdiagram"
        ):
            return "er"

        raise ValueError(
            "Unable to determine Mermaid diagram type"
        )

    # ---------------------------------------------------------
    # Flowchart
    # ---------------------------------------------------------

    def _parse_flowchart(
        self,
        diagram: DiagramIR,
        lines: List[str],
    ) -> None:
        for line in lines[1:]:
            if line.startswith(
                "%%"
            ):
                continue

            statements = self._split_flow_statements(
                line
            )

            for statement in statements:
                self._parse_flow_statement(
                    diagram,
                    statement,
                )

    def _split_flow_statements(
        self,
        line: str,
    ) -> List[str]:
        # Mermaid permits multiple statements
        # separated by semicolons.
        return [
            item.strip()
            for item in line.split(";")
            if item.strip()
        ]

    def _parse_flow_statement(
        self,
        diagram: DiagramIR,
        statement: str,
    ) -> None:
        edge_match = re.search(
            r"(.+?)\s+((?:-->|---|-.->|==>|--o|--x|~~~|-.->))\s+(.+)",
            statement,
        )

        if edge_match:
            left = edge_match.group(1).strip()
            operator = edge_match.group(2).strip()
            right = edge_match.group(3).strip()

            source_id, source_label = (
                self._parse_flow_node(
                    left
                )
            )

            target_id, target_label = (
                self._parse_flow_node(
                    right
                )
            )

            self._ensure_node(
                diagram,
                source_id,
                source_label,
            )

            self._ensure_node(
                diagram,
                target_id,
                target_label,
            )

            edge_id = (
                f"{source_id}"
                f"__"
                f"{target_id}"
            )

            self._add_edge(
                diagram,
                self._make_edge(
                    edge_id,
                    source_id,
                    target_id,
                    operator,
                ),
            )

            return

        node_id, label = (
            self._parse_flow_node(
                statement
            )
        )

        if node_id:
            self._ensure_node(
                diagram,
                node_id,
                label,
            )

    def _parse_flow_node(
        self,
        value: str,
    ) -> Tuple[str, str]:
        value = value.strip()

        patterns = [
            r"^([A-Za-z0-9_-]+)\[(.*?)\]$",
            r"^([A-Za-z0-9_-]+)\((.*?)\)$",
            r"^([A-Za-z0-9_-]+)\{(.*?)\}$",
            r"^([A-Za-z0-9_-]+)\[\[(.*?)\]\]$",
            r"^([A-Za-z0-9_-]+)$",
        ]

        for pattern in patterns:
            match = re.match(
                pattern,
                value,
            )

            if not match:
                continue

            node_id = match.group(1)

            label = (
                match.group(2)
                if match.lastindex
                and match.lastindex >= 2
                else node_id
            )

            return (
                node_id,
                self._strip_quotes(
                    label
                ),
            )

        return (
            value,
            value,
        )

    # ---------------------------------------------------------
    # Sequence
    # ---------------------------------------------------------

    def _parse_sequence(
        self,
        diagram: DiagramIR,
        lines: List[str],
    ) -> None:
        participants: Dict[
            str,
            str,
        ] = {}

        edge_counter = 0

        for line in lines[1:]:
            if line.startswith(
                "%%"
            ):
                continue

            participant_match = re.match(
                r"participant\s+(\S+)(?:\s+as\s+(.+))?",
                line,
                re.IGNORECASE,
            )

            if participant_match:
                identifier = (
                    participant_match.group(1)
                )

                label = (
                    participant_match.group(2)
                    or identifier
                )

                participants[
                    identifier
                ] = label

                self._ensure_node(
                    diagram,
                    identifier,
                    label,
                )

                continue

            message_match = re.match(
                r"(\S+?)\s*([-]+>|-->|->>|-x|--x)\s*(\S+?)\s*:\s*(.*)",
                line,
            )

            if not message_match:
                continue

            source = (
                message_match.group(1)
            )

            target = (
                message_match.group(3)
            )

            label = (
                message_match.group(4)
            )

            self._ensure_node(
                diagram,
                source,
                participants.get(
                    source,
                    source,
                ),
            )

            self._ensure_node(
                diagram,
                target,
                participants.get(
                    target,
                    target,
                ),
            )

            edge_counter += 1

            self._add_edge(
                diagram,
                self._make_edge(
                    f"message_{edge_counter}",
                    source,
                    target,
                    label,
                ),
            )

    # ---------------------------------------------------------
    # State
    # ---------------------------------------------------------

    def _parse_state(
        self,
        diagram: DiagramIR,
        lines: List[str],
    ) -> None:
        counter = 0

        for line in lines[1:]:
            line = line.strip()

            if line.startswith(
                "%%"
            ):
                continue

            if line.startswith(
                "[*]"
            ):
                source = "__start__"
                self._ensure_node(
                    diagram,
                    source,
                    "Start",
                )
            else:
                match = re.match(
                    r"(.+?)\s*-->\s*(.+?)(?::\s*(.*))?$",
                    line,
                )

                if not match:
                    continue

                source = self._clean_state(
                    match.group(1)
                )

                target = self._clean_state(
                    match.group(2)
                )

                label = (
                    match.group(3)
                    or ""
                )

                self._ensure_node(
                    diagram,
                    source,
                    source,
                )

                self._ensure_node(
                    diagram,
                    target,
                    target,
                )

                counter += 1

                self._add_edge(
                    diagram,
                    self._make_edge(
                        f"state_{counter}",
                        source,
                        target,
                        label,
                    ),
                )

    # ---------------------------------------------------------
    # Class Diagram
    # ---------------------------------------------------------

    def _parse_class(
        self,
        diagram: DiagramIR,
        lines: List[str],
    ) -> None:
        counter = 0

        for line in lines[1:]:
            line = line.strip()

            class_match = re.match(
                r"class\s+([A-Za-z0-9_]+)",
                line,
                re.IGNORECASE,
            )

            if class_match:
                class_name = (
                    class_match.group(1)
                )

                self._ensure_node(
                    diagram,
                    class_name,
                    class_name,
                )

                continue

            relation_match = re.match(
                r"([A-Za-z0-9_]+)\s+([-.]+[|o*<>]*[-.]+)\s+([A-Za-z0-9_]+)(?:\s*:\s*(.*))?",
                line,
            )

            if relation_match:
                source = (
                    relation_match.group(1)
                )

                target = (
                    relation_match.group(3)
                )

                label = (
                    relation_match.group(4)
                    or ""
                )

                self._ensure_node(
                    diagram,
                    source,
                    source,
                )

                self._ensure_node(
                    diagram,
                    target,
                    target,
                )

                counter += 1

                self._add_edge(
                    diagram,
                    self._make_edge(
                        f"class_{counter}",
                        source,
                        target,
                        label,
                    ),
                )

    # ---------------------------------------------------------
    # ER Diagram
    # ---------------------------------------------------------

    def _parse_er(
        self,
        diagram: DiagramIR,
        lines: List[str],
    ) -> None:
        counter = 0

        relation_pattern = re.compile(
            r"([A-Za-z0-9_]+)\s+([|o}]{1,2}--[|o{]{1,2})\s+([A-Za-z0-9_]+)(?:\s*:\s*(.*))?"
        )

        for line in lines[1:]:
            line = line.strip()

            match = relation_pattern.match(
                line
            )

            if not match:
                continue

            source = match.group(1)
            target = match.group(3)

            label = (
                match.group(4)
                or ""
            )

            self._ensure_node(
                diagram,
                source,
                source,
            )

            self._ensure_node(
                diagram,
                target,
                target,
            )

            counter += 1

            self._add_edge(
                diagram,
                self._make_edge(
                    f"relation_{counter}",
                    source,
                    target,
                    label,
                ),
            )

    # ---------------------------------------------------------
    # Helpers
    # ---------------------------------------------------------

    def _ensure_node(
        self,
        diagram: DiagramIR,
        node_id: str,
        label: str,
    ) -> None:
        nodes = getattr(
            diagram,
            "nodes",
            [],
        )

        if isinstance(nodes, dict):
            if node_id in nodes:
                return
        else:
            for node in nodes:
                if str(
                    getattr(
                        node,
                        "id",
                        "",
                    )
                ) == node_id:
                    return

        node = IRNode(
            id=node_id,
            label=label or node_id,
        )

        self._add_node(
            diagram,
            node,
        )

    def _make_edge(
        self,
        edge_id: str,
        source: str,
        target: str,
        label: str,
    ) -> IREdge:
        try:
            return IREdge(
                id=edge_id,
                source=source,
                target=target,
                label=label,
            )
        except TypeError:
            return IREdge(
                id=edge_id,
                source_id=source,
                target_id=target,
                label=label,
            )

    def _add_node(
        self,
        diagram: DiagramIR,
        node: IRNode,
    ) -> None:
        nodes = getattr(
            diagram,
            "nodes",
            None,
        )

        if isinstance(nodes, dict):
            nodes[node.id] = node
        else:
            nodes.append(node)

    def _add_edge(
        self,
        diagram: DiagramIR,
        edge: IREdge,
    ) -> None:
        edges = getattr(
            diagram,
            "edges",
            None,
        )

        edge_id = getattr(
            edge,
            "id",
            None,
        )

        if isinstance(edges, dict):
            edges[edge_id] = edge
        else:
            edges.append(edge)

    def _strip_quotes(
        self,
        value: str,
    ) -> str:
        return value.strip(
            "\"'"
        )

    def _clean_state(
        self,
        value: str,
    ) -> str:
        value = value.strip()

        if value == "[*]":
            return "__end__"

        return value