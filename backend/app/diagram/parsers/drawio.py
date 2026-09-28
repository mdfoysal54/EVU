from __future__ import annotations

import re
import xml.etree.ElementTree as ET
from typing import Any, Dict, Optional

from ..ir.diagram import DiagramIR
from ..ir.nodes import IRNode
from ..ir.edges import IREdge


class DrawioParser:
    """
    Parser for diagrams produced by diagrams.net / draw.io.

    Supports:
    - mxGraphModel
    - mxCell vertices
    - mxCell edges
    - geometry
    - labels
    - styles
    """

    def parse(
        self,
        source: str,
    ) -> DiagramIR:
        if not source or not source.strip():
            raise ValueError(
                "Draw.io source cannot be empty"
            )

        xml_source = self._decode_source(
            source
        )

        try:
            root = ET.fromstring(
                xml_source
            )
        except ET.ParseError as exc:
            raise ValueError(
                f"Invalid Draw.io XML: {exc}"
            ) from exc

        diagram = DiagramIR()

        cells = self._find_cells(root)

        for cell in cells:
            if self._is_edge(cell):
                self._parse_edge(
                    diagram,
                    cell,
                )
            elif self._is_vertex(cell):
                self._parse_vertex(
                    diagram,
                    cell,
                )

        return diagram

    def _decode_source(
        self,
        source: str,
    ) -> str:
        source = source.strip()

        if source.startswith(
            "<mxGraphModel"
        ):
            return source

        if source.startswith(
            "<mxfile"
        ):
            return source

        # Some Draw.io exports may wrap XML
        # in HTML entities.
        return source

    def _find_cells(
        self,
        root: ET.Element,
    ) -> list[ET.Element]:
        return [
            element
            for element in root.iter()
            if self._local_name(
                element.tag
            )
            == "mxCell"
        ]

    def _local_name(
        self,
        tag: str,
    ) -> str:
        if "}" in tag:
            return tag.rsplit(
                "}",
                1,
            )[-1]

        return tag

    def _is_edge(
        self,
        cell: ET.Element,
    ) -> bool:
        return (
            cell.attrib.get("edge")
            == "1"
        )

    def _is_vertex(
        self,
        cell: ET.Element,
    ) -> bool:
        return (
            cell.attrib.get("vertex")
            == "1"
        )

    def _parse_vertex(
        self,
        diagram: DiagramIR,
        cell: ET.Element,
    ) -> None:
        node_id = cell.attrib.get(
            "id"
        )

        if not node_id:
            return

        label = cell.attrib.get(
            "value",
            "",
        )

        style = cell.attrib.get(
            "style",
            "",
        )

        geometry = self._geometry(
            cell
        )

        node = self._create_node(
            node_id=node_id,
            label=self._clean_label(
                label
            ),
            geometry=geometry,
            style=style,
        )

        self._add_node(
            diagram,
            node,
        )

    def _parse_edge(
        self,
        diagram: DiagramIR,
        cell: ET.Element,
    ) -> None:
        edge_id = cell.attrib.get(
            "id"
        )

        source = cell.attrib.get(
            "source"
        )

        target = cell.attrib.get(
            "target"
        )

        if not edge_id:
            return

        if not source or not target:
            return

        label = self._clean_label(
            cell.attrib.get(
                "value",
                "",
            )
        )

        edge = self._create_edge(
            edge_id=edge_id,
            source=source,
            target=target,
            label=label,
        )

        self._add_edge(
            diagram,
            edge,
        )

    def _geometry(
        self,
        cell: ET.Element,
    ) -> Dict[str, float]:
        for child in cell:
            if (
                self._local_name(
                    child.tag
                )
                == "mxGeometry"
            ):
                return {
                    "x": self._float(
                        child.attrib.get(
                            "x"
                        )
                    ),
                    "y": self._float(
                        child.attrib.get(
                            "y"
                        )
                    ),
                    "width": self._float(
                        child.attrib.get(
                            "width"
                        )
                    ),
                    "height": self._float(
                        child.attrib.get(
                            "height"
                        )
                    ),
                }

        return {
            "x": 0.0,
            "y": 0.0,
            "width": 120.0,
            "height": 60.0,
        }

    def _float(
        self,
        value: Optional[str],
    ) -> float:
        if value is None:
            return 0.0

        try:
            return float(value)
        except ValueError:
            return 0.0

    def _clean_label(
        self,
        label: str,
    ) -> str:
        if not label:
            return ""

        label = re.sub(
            r"<[^>]+>",
            "",
            label,
        )

        return (
            label
            .replace("&lt;", "<")
            .replace("&gt;", ">")
            .replace("&amp;", "&")
            .strip()
        )

    def _create_node(
        self,
        node_id: str,
        label: str,
        geometry: Dict[str, float],
        style: str,
    ) -> IRNode:
        node = IRNode(
            id=node_id,
            label=label,
        )

        self._apply_geometry(
            node,
            geometry,
        )

        self._apply_style(
            node,
            style,
        )

        return node

    def _apply_geometry(
        self,
        node: IRNode,
        geometry: Dict[str, float],
    ) -> None:
        for key in (
            "x",
            "y",
            "width",
            "height",
        ):
            value = geometry.get(key)

            if hasattr(node, key):
                setattr(
                    node,
                    key,
                    value,
                )

        position = getattr(
            node,
            "position",
            None,
        )

        if isinstance(position, dict):
            position.update(
                {
                    "x": geometry["x"],
                    "y": geometry["y"],
                }
            )

    def _apply_style(
        self,
        node: IRNode,
        style: str,
    ) -> None:
        if not style:
            return

        metadata = getattr(
            node,
            "metadata",
            None,
        )

        if isinstance(metadata, dict):
            metadata[
                "drawio_style"
            ] = style

    def _create_edge(
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