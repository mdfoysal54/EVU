from __future__ import annotations

import math
import random
from dataclasses import dataclass
from typing import Dict, List, Tuple

from ..ir.diagram import DiagramIR
from ..ir.nodes import IRNode
from ..ir.edges import IREdge


@dataclass
class ForceLayoutConfig:
    """
    Configuration for force-directed graph layout.
    """

    width: float = 1200.0
    height: float = 800.0

    iterations: int = 200

    repulsion: float = 5000.0
    attraction: float = 0.08

    ideal_edge_length: float = 160.0

    gravity: float = 0.01
    damping: float = 0.85

    node_radius: float = 35.0

    seed: int = 42

    min_x: float = 20.0
    min_y: float = 20.0

    def validate(self) -> None:
        if self.width <= 0:
            raise ValueError("width must be greater than zero")

        if self.height <= 0:
            raise ValueError("height must be greater than zero")

        if self.iterations < 1:
            raise ValueError("iterations must be at least 1")

        if self.repulsion < 0:
            raise ValueError("repulsion cannot be negative")

        if self.attraction < 0:
            raise ValueError("attraction cannot be negative")

        if self.ideal_edge_length <= 0:
            raise ValueError("ideal_edge_length must be greater than zero")


@dataclass
class ForcePosition:
    x: float
    y: float


class ForceLayout:
    """
    Lightweight deterministic force-directed layout.

    The implementation intentionally has no dependency on NetworkX or
    another graph library so EVU can use it as a standalone engine.
    """

    def __init__(
        self,
        config: ForceLayoutConfig | None = None,
    ) -> None:
        self.config = config or ForceLayoutConfig()
        self.config.validate()

    def layout(
        self,
        diagram: DiagramIR,
    ) -> DiagramIR:
        nodes = list(self._nodes(diagram))
        edges = list(self._edges(diagram))

        if not nodes:
            return diagram

        positions = self._initial_positions(nodes)
        velocities: Dict[str, Tuple[float, float]] = {
            node_id: (0.0, 0.0)
            for node_id in positions
        }

        adjacency = self._build_adjacency(edges)

        for _ in range(self.config.iterations):
            forces = {
                node_id: [0.0, 0.0]
                for node_id in positions
            }

            self._apply_repulsion(
                positions,
                forces,
            )

            self._apply_attraction(
                positions,
                forces,
                adjacency,
            )

            self._apply_gravity(
                positions,
                forces,
            )

            self._integrate(
                positions,
                velocities,
                forces,
            )

        self._write_positions(diagram, positions)

        return diagram

    def _nodes(
        self,
        diagram: DiagramIR,
    ) -> List[IRNode]:
        nodes = getattr(diagram, "nodes", None)

        if nodes is None:
            return []

        if isinstance(nodes, dict):
            return list(nodes.values())

        return list(nodes)

    def _edges(
        self,
        diagram: DiagramIR,
    ) -> List[IREdge]:
        edges = getattr(diagram, "edges", None)

        if edges is None:
            return []

        if isinstance(edges, dict):
            return list(edges.values())

        return list(edges)

    def _node_id(
        self,
        node: IRNode,
    ) -> str:
        value = getattr(node, "id", None)

        if value is None:
            value = getattr(node, "node_id", None)

        return str(value)

    def _initial_positions(
        self,
        nodes: List[IRNode],
    ) -> Dict[str, ForcePosition]:
        rng = random.Random(self.config.seed)

        result: Dict[str, ForcePosition] = {}

        center_x = self.config.width / 2
        center_y = self.config.height / 2

        radius = min(
            self.config.width,
            self.config.height,
        ) * 0.30

        total = max(len(nodes), 1)

        for index, node in enumerate(nodes):
            node_id = self._node_id(node)

            angle = (
                2.0
                * math.pi
                * index
                / total
            )

            jitter_x = rng.uniform(-20.0, 20.0)
            jitter_y = rng.uniform(-20.0, 20.0)

            result[node_id] = ForcePosition(
                x=center_x
                + math.cos(angle) * radius
                + jitter_x,
                y=center_y
                + math.sin(angle) * radius
                + jitter_y,
            )

        return result

    def _build_adjacency(
        self,
        edges: List[IREdge],
    ) -> List[Tuple[str, str]]:
        adjacency: List[Tuple[str, str]] = []

        for edge in edges:
            source = self._edge_endpoint(
                edge,
                "source",
            )

            target = self._edge_endpoint(
                edge,
                "target",
            )

            if source is None or target is None:
                continue

            adjacency.append(
                (source, target)
            )

        return adjacency

    def _edge_endpoint(
        self,
        edge: IREdge,
        name: str,
    ) -> str | None:
        value = getattr(edge, name, None)

        if value is None:
            value = getattr(
                edge,
                f"{name}_id",
                None,
            )

        if value is None:
            return None

        return str(value)

    def _apply_repulsion(
        self,
        positions: Dict[str, ForcePosition],
        forces: Dict[str, List[float]],
    ) -> None:
        ids = list(positions.keys())

        for i in range(len(ids)):
            a = ids[i]

            for j in range(i + 1, len(ids)):
                b = ids[j]

                pa = positions[a]
                pb = positions[b]

                dx = pa.x - pb.x
                dy = pa.y - pb.y

                distance_sq = (
                    dx * dx
                    + dy * dy
                )

                if distance_sq < 1e-6:
                    dx = 0.01
                    dy = 0.01
                    distance_sq = 0.0002

                distance = math.sqrt(
                    distance_sq
                )

                force = (
                    self.config.repulsion
                    / distance_sq
                )

                fx = (
                    dx
                    / distance
                    * force
                )

                fy = (
                    dy
                    / distance
                    * force
                )

                forces[a][0] += fx
                forces[a][1] += fy

                forces[b][0] -= fx
                forces[b][1] -= fy

    def _apply_attraction(
        self,
        positions: Dict[str, ForcePosition],
        forces: Dict[str, List[float]],
        adjacency: List[Tuple[str, str]],
    ) -> None:
        for source, target in adjacency:
            if source not in positions:
                continue

            if target not in positions:
                continue

            a = positions[source]
            b = positions[target]

            dx = b.x - a.x
            dy = b.y - a.y

            distance = math.sqrt(
                dx * dx + dy * dy
            )

            if distance < 1e-6:
                continue

            displacement = (
                distance
                - self.config.ideal_edge_length
            )

            force = (
                displacement
                * self.config.attraction
            )

            fx = (
                dx
                / distance
                * force
            )

            fy = (
                dy
                / distance
                * force
            )

            forces[source][0] += fx
            forces[source][1] += fy

            forces[target][0] -= fx
            forces[target][1] -= fy

    def _apply_gravity(
        self,
        positions: Dict[str, ForcePosition],
        forces: Dict[str, List[float]],
    ) -> None:
        center_x = self.config.width / 2
        center_y = self.config.height / 2

        for node_id, position in positions.items():
            forces[node_id][0] += (
                center_x - position.x
            ) * self.config.gravity

            forces[node_id][1] += (
                center_y - position.y
            ) * self.config.gravity

    def _integrate(
        self,
        positions: Dict[str, ForcePosition],
        velocities: Dict[str, Tuple[float, float]],
        forces: Dict[str, List[float]],
    ) -> None:
        for node_id, position in positions.items():
            old_vx, old_vy = velocities[node_id]

            vx = (
                old_vx
                + forces[node_id][0]
            ) * self.config.damping

            vy = (
                old_vy
                + forces[node_id][1]
            ) * self.config.damping

            max_velocity = 40.0

            vx = max(
                -max_velocity,
                min(max_velocity, vx),
            )

            vy = max(
                -max_velocity,
                min(max_velocity, vy),
            )

            velocities[node_id] = (
                vx,
                vy,
            )

            position.x += vx
            position.y += vy

            self._clamp_position(position)

    def _clamp_position(
        self,
        position: ForcePosition,
    ) -> None:
        margin = self.config.node_radius

        position.x = max(
            self.config.min_x + margin,
            min(
                self.config.width
                - margin,
                position.x,
            ),
        )

        position.y = max(
            self.config.min_y + margin,
            min(
                self.config.height
                - margin,
                position.y,
            ),
        )

    def _write_positions(
        self,
        diagram: DiagramIR,
        positions: Dict[str, ForcePosition],
    ) -> None:
        nodes = getattr(
            diagram,
            "nodes",
            [],
        )

        if isinstance(nodes, dict):
            iterable = nodes.values()
        else:
            iterable = nodes

        for node in iterable:
            node_id = self._node_id(node)

            position = positions.get(node_id)

            if position is None:
                continue

            self._set_position(
                node,
                position.x,
                position.y,
            )

    def _set_position(
        self,
        node: IRNode,
        x: float,
        y: float,
    ) -> None:
        if hasattr(node, "x"):
            setattr(node, "x", x)

        if hasattr(node, "y"):
            setattr(node, "y", y)

        position = getattr(
            node,
            "position",
            None,
        )

        if isinstance(position, dict):
            position["x"] = x
            position["y"] = y

        elif position is not None:
            if hasattr(position, "x"):
                position.x = x

            if hasattr(position, "y"):
                position.y = y