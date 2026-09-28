from __future__ import annotations

import json
from typing import Any, Dict

from ..ir.diagram import DiagramIR
from ..ir.nodes import IRNode
from ..ir.edges import IREdge


class ExcalidrawParser:
    """
    Parser for Excalidraw JSON.

    Converts common Excalidraw elements into EVU IR.

    Supported:
    - rectangle
    - ellipse
    - diamond
    - text
    - arrows
    - lines
    """

    def parse(
        self,
        source: str | Dict[str, Any],
    ) -> DiagramIR:
        data = self._load(source)

        elements = data.get(
            "elements",
            [],
        )

        diagram = DiagramIR()

        for element in elements:
            if not isinstance(
                element,
                dict,
            ):
                continue

            if element.get(
                "isDeleted",
                False,
            ):
                continue

            element_type = element.get(
                "type",
                "",
            )

            if element_type in {
                "rectangle",
                "ellipse",
                "diamond",
                "text",
            }:
                self._parse_node(
                    diagram,
                    element,
                )

            elif element_type in {
                "arrow",
                "line",
            }:
                self._parse_edge(
                    diagram,
                    element,
                )

        return diagram

    def _load(
        self,
        source: str | Dict[str, Any],
    ) -> Dict[str, Any]:
        if isinstance(
            source,
            dict,
        ):
            return source

        if not source.strip():
            raise ValueError(
                "Excalidraw source cannot be empty"
            )

        try:
            value = json.loads(source)
        except json.JSONDecodeError as exc:
            raise ValueError(
                f"Invalid Excalidraw JSON: {exc}"
            ) from exc

        if not isinstance(
            value,
            dict,
        ):
            raise ValueError(
                "Excalidraw document must be an object"
            )

        return value

    def _parse_node(
        self,
        diagram: DiagramIR,
        element: Dict[str, Any],
    ) -> None:
        element_id = str(
            element.get(
                "id",
                "",
            )
        )

        if not element_id:
            return

        node = IRNode(
            id=element_id,
            label=self._label(
                element
            ),
        )

        self._set_if_exists(
            node,
            "x",
            self._number(
                element.get("x")
            ),
        )

        self._set_if_exists(
            node,
            "y",
            self._number(
                element.get("y")
            ),
        )

        self._set_if_exists(
            node,
            "width",
            self._number(
                element.get("width")
            ),
        )

        self._set_if_exists(
            node,
            "height",
            self._number(
                element.get("height")
            ),
        )

        metadata = getattr(
            node,
            "metadata",
            None,
        )

        if isinstance(metadata, dict):
            metadata[
                "excalidraw_type"
            ] = element.get(
                "type"
            )

            metadata[
                "background_color"
            ] = element.get(
                "backgroundColor"
            )

            metadata[
                "stroke_color"
            ] = element.get(
                "strokeColor"
            )

        self._add_node(
            diagram,
            node,
        )

    def _parse_edge(
        self,
        diagram: DiagramIR,
        element: Dict[str, Any],
    ) -> None:
        edge_id = str(
            element.get(
                "id",
                "",
            )
        )

        if not edge_id:
            return

        start_id = (
            element.get(
                "startBinding",
                {}
            )
            or {}
        ).get(
            "elementId"
        )

        end_id = (
            element.get(
                "endBinding",
                {}
            )
            or {}
        ).get(
            "elementId"
        )

        points = element.get(
            "points",
            [],
        )

        if not start_id or not end_id:
            start_id, end_id = (
                self._infer_endpoints(
                    points,
                    diagram,
                )
            )

        if not start_id or not end_id:
            return

        try:
            edge = IREdge(
                id=edge_id,
                source=str(start_id),
                target=str(end_id),
                label="",
            )
        except TypeError:
            edge = IREdge(
                id=edge_id,
                source_id=str(start_id),
                target_id=str(end_id),
                label="",
            )

        metadata = getattr(
            edge,
            "metadata",
            None,
        )

        if isinstance(metadata, dict):
            metadata[
                "excalidraw_type"
            ] = element.get(
                "type"
            )

            metadata[
                "points"
            ] = points

            metadata[
                "start_arrowhead"
            ] = element.get(
                "startArrowhead"
            )

            metadata[
                "end_arrowhead"
            ] = element.get(
                "endArrowhead"
            )

        self._add_edge(
            diagram,
            edge,
        )

    def _infer_endpoints(
        self,
        points: Any,
        diagram: DiagramIR,
    ) -> tuple[str | None, str | None]:
        if not isinstance(
            points,
            list,
        ):
            return None, None

        if len(points) < 2:
            return None, None

        first = points[0]
        last = points[-1]

        if (
            not isinstance(
                first,
                (list, tuple),
            )
            or not isinstance(
                last,
                (list, tuple),
            )
        ):
            return None, None

        first_xy = (
            float(first[0]),
            float(first[1]),
        )

        last_xy = (
            float(last[0]),
            float(last[1]),
        )

        nodes = getattr(
            diagram,
            "nodes",
            [],
        )

        iterable = (
            nodes.values()
            if isinstance(
                nodes,
                dict,
            )
            else nodes
        )

        start = None
        end = None

        start_distance = float("inf")
        end_distance = float("inf")

        for node in iterable:
            node_id = str(
                getattr(
                    node,
                    "id",
                    "",
                )
            )

            x = self._number(
                getattr(
                    node,
                    "x",
                    0,
                )
            )

            y = self._number(
                getattr(
                    node,
                    "y",
                    0,
                )
            )

            width = self._number(
                getattr(
                    node,
                    "width",
                    0,
                )
            )

            height = self._number(
                getattr(
                    node,
                    "height",
                    0,
                )
            )

            center = (
                x + width / 2,
                y + height / 2,
            )

            d1 = self._distance(
                first_xy,
                center,
            )

            d2 = self._distance(
                last_xy,
                center,
            )

            if d1 < start_distance:
                start_distance = d1
                start = node_id

            if d2 < end_distance:
                end_distance = d2
                end = node_id

        return start, end

    def _label(
        self,
        element: Dict[str, Any],
    ) -> str:
        text = element.get(
            "text",
            "",
        )

        if text:
            return str(text)

        return str(
            element.get(
                "customData",
                "",
            )
            or ""
        )

    def _number(
        self,
        value: Any,
    ) -> float:
        try:
            return float(value or 0)
        except (
            TypeError,
            ValueError,
        ):
            return 0.0

    def _distance(
        self,
        a: tuple[float, float],
        b: tuple[float, float],
    ) -> float:
        dx = a[0] - b[0]
        dy = a[1] - b[1]

        return (
            dx * dx
            + dy * dy
        ) ** 0.5

    def _set_if_exists(
        self,
        obj: Any,
        name: str,
        value: Any,
    ) -> None:
        if hasattr(obj, name):
            setattr(
                obj,
                name,
                value,
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