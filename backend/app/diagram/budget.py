from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, Optional


class BudgetExceededError(RuntimeError):
    """Raised when a diagram operation exceeds its configured budget."""


class BudgetDimension(str, Enum):
    NODES = "nodes"
    EDGES = "edges"
    GROUPS = "groups"
    TOKENS = "tokens"
    BYTES = "bytes"
    RENDER_TIME = "render_time"
    OPERATIONS = "operations"


@dataclass
class DiagramBudgetConfig:
    """
    Resource limits used by the diagram engine.

    These limits protect EVU from excessively large diagrams,
    expensive rendering operations, and untrusted imported data.
    """

    max_nodes: int = 5000
    max_edges: int = 10000
    max_groups: int = 1000

    max_tokens: int = 100000
    max_input_bytes: int = 5 * 1024 * 1024

    max_render_time_ms: float = 30000.0
    max_operations: int = 100000

    max_diagram_width: float = 10000.0
    max_diagram_height: float = 10000.0

    def validate(self) -> None:
        values = {
            "max_nodes": self.max_nodes,
            "max_edges": self.max_edges,
            "max_groups": self.max_groups,
            "max_tokens": self.max_tokens,
            "max_input_bytes": self.max_input_bytes,
            "max_operations": self.max_operations,
        }

        for name, value in values.items():
            if value < 0:
                raise ValueError(
                    f"{name} cannot be negative"
                )

        if self.max_render_time_ms < 0:
            raise ValueError(
                "max_render_time_ms cannot be negative"
            )

        if self.max_diagram_width <= 0:
            raise ValueError(
                "max_diagram_width must be positive"
            )

        if self.max_diagram_height <= 0:
            raise ValueError(
                "max_diagram_height must be positive"
            )


@dataclass
class DiagramBudgetUsage:
    """
    Current resource consumption.
    """

    nodes: int = 0
    edges: int = 0
    groups: int = 0
    tokens: int = 0
    input_bytes: int = 0
    render_time_ms: float = 0.0
    operations: int = 0

    def copy(self) -> "DiagramBudgetUsage":
        return DiagramBudgetUsage(
            nodes=self.nodes,
            edges=self.edges,
            groups=self.groups,
            tokens=self.tokens,
            input_bytes=self.input_bytes,
            render_time_ms=self.render_time_ms,
            operations=self.operations,
        )

    def as_dict(self) -> Dict[str, Any]:
        return {
            "nodes": self.nodes,
            "edges": self.edges,
            "groups": self.groups,
            "tokens": self.tokens,
            "input_bytes": self.input_bytes,
            "render_time_ms": self.render_time_ms,
            "operations": self.operations,
        }


@dataclass
class BudgetCheckResult:
    """
    Result returned by budget checks.
    """

    allowed: bool
    dimension: Optional[BudgetDimension] = None
    current: float = 0
    requested: float = 0
    limit: float = 0
    message: str = ""

    def raise_if_exceeded(self) -> None:
        if not self.allowed:
            raise BudgetExceededError(
                self.message
            )


class DiagramBudget:
    """
    Tracks and enforces diagram resource consumption.

    Usage example:

        budget = DiagramBudget()

        budget.reserve_nodes(10)
        budget.reserve_edges(12)

        budget.consume_tokens(1000)

        budget.assert_within_limits()
    """

    def __init__(
        self,
        config: DiagramBudgetConfig | None = None,
    ) -> None:
        self.config = (
            config
            or DiagramBudgetConfig()
        )

        self.config.validate()

        self.usage = DiagramBudgetUsage()

    # ---------------------------------------------------------
    # Generic checks
    # ---------------------------------------------------------

    def check(
        self,
        dimension: BudgetDimension,
        amount: float = 1,
    ) -> BudgetCheckResult:
        if amount < 0:
            raise ValueError(
                "Budget amount cannot be negative"
            )

        current, limit = self._values(
            dimension
        )

        allowed = (
            current + amount
            <= limit
        )

        if allowed:
            message = ""
        else:
            message = (
                f"Diagram budget exceeded for "
                f"{dimension.value}: "
                f"current={current}, "
                f"requested={amount}, "
                f"limit={limit}"
            )

        return BudgetCheckResult(
            allowed=allowed,
            dimension=dimension,
            current=current,
            requested=amount,
            limit=limit,
            message=message,
        )

    def consume(
        self,
        dimension: BudgetDimension,
        amount: float = 1,
    ) -> None:
        result = self.check(
            dimension,
            amount,
        )

        result.raise_if_exceeded()

        self._increment(
            dimension,
            amount,
        )

    def try_consume(
        self,
        dimension: BudgetDimension,
        amount: float = 1,
    ) -> bool:
        result = self.check(
            dimension,
            amount,
        )

        if not result.allowed:
            return False

        self._increment(
            dimension,
            amount,
        )

        return True

    # ---------------------------------------------------------
    # Nodes
    # ---------------------------------------------------------

    def reserve_nodes(
        self,
        count: int = 1,
    ) -> None:
        self.consume(
            BudgetDimension.NODES,
            count,
        )

    def can_add_nodes(
        self,
        count: int = 1,
    ) -> bool:
        return self.check(
            BudgetDimension.NODES,
            count,
        ).allowed

    # ---------------------------------------------------------
    # Edges
    # ---------------------------------------------------------

    def reserve_edges(
        self,
        count: int = 1,
    ) -> None:
        self.consume(
            BudgetDimension.EDGES,
            count,
        )

    def can_add_edges(
        self,
        count: int = 1,
    ) -> bool:
        return self.check(
            BudgetDimension.EDGES,
            count,
        ).allowed

    # ---------------------------------------------------------
    # Groups
    # ---------------------------------------------------------

    def reserve_groups(
        self,
        count: int = 1,
    ) -> None:
        self.consume(
            BudgetDimension.GROUPS,
            count,
        )

    def can_add_groups(
        self,
        count: int = 1,
    ) -> bool:
        return self.check(
            BudgetDimension.GROUPS,
            count,
        ).allowed

    # ---------------------------------------------------------
    # Tokens
    # ---------------------------------------------------------

    def consume_tokens(
        self,
        count: int,
    ) -> None:
        self.consume(
            BudgetDimension.TOKENS,
            count,
        )

    def can_consume_tokens(
        self,
        count: int,
    ) -> bool:
        return self.check(
            BudgetDimension.TOKENS,
            count,
        ).allowed

    # ---------------------------------------------------------
    # Input
    # ---------------------------------------------------------

    def register_input(
        self,
        data: str | bytes,
    ) -> None:
        if isinstance(
            data,
            str,
        ):
            size = len(
                data.encode("utf-8")
            )
        else:
            size = len(data)

        self.consume(
            BudgetDimension.BYTES,
            size,
        )

        self.usage.input_bytes = (
            self.usage.input_bytes
        )

    def check_input_size(
        self,
        data: str | bytes,
    ) -> bool:
        if isinstance(
            data,
            str,
        ):
            size = len(
                data.encode("utf-8")
            )
        else:
            size = len(data)

        return self.check(
            BudgetDimension.BYTES,
            size,
        ).allowed

    # ---------------------------------------------------------
    # Operations
    # ---------------------------------------------------------

    def operation(
        self,
        count: int = 1,
    ) -> None:
        self.consume(
            BudgetDimension.OPERATIONS,
            count,
        )

    # ---------------------------------------------------------
    # Render time
    # ---------------------------------------------------------

    def add_render_time(
        self,
        milliseconds: float,
    ) -> None:
        self.consume(
            BudgetDimension.RENDER_TIME,
            milliseconds,
        )

    def can_render_for(
        self,
        milliseconds: float,
    ) -> bool:
        return self.check(
            BudgetDimension.RENDER_TIME,
            milliseconds,
        ).allowed

    # ---------------------------------------------------------
    # Diagram dimensions
    # ---------------------------------------------------------

    def validate_dimensions(
        self,
        width: float,
        height: float,
    ) -> None:
        if width < 0 or height < 0:
            raise BudgetExceededError(
                "Diagram dimensions cannot be negative"
            )

        if width > self.config.max_diagram_width:
            raise BudgetExceededError(
                f"Diagram width {width} exceeds "
                f"maximum {self.config.max_diagram_width}"
            )

        if height > self.config.max_diagram_height:
            raise BudgetExceededError(
                f"Diagram height {height} exceeds "
                f"maximum {self.config.max_diagram_height}"
            )

    # ---------------------------------------------------------
    # Diagram inspection
    # ---------------------------------------------------------

    def estimate_diagram(
        self,
        diagram: Any,
    ) -> DiagramBudgetUsage:
        nodes = getattr(
            diagram,
            "nodes",
            [],
        )

        edges = getattr(
            diagram,
            "edges",
            [],
        )

        groups = getattr(
            diagram,
            "groups",
            [],
        )

        node_count = self._collection_length(
            nodes
        )

        edge_count = self._collection_length(
            edges
        )

        group_count = self._collection_length(
            groups
        )

        return DiagramBudgetUsage(
            nodes=node_count,
            edges=edge_count,
            groups=group_count,
        )

    def validate_diagram(
        self,
        diagram: Any,
    ) -> None:
        usage = self.estimate_diagram(
            diagram
        )

        checks = [
            (
                BudgetDimension.NODES,
                usage.nodes,
            ),
            (
                BudgetDimension.EDGES,
                usage.edges,
            ),
            (
                BudgetDimension.GROUPS,
                usage.groups,
            ),
        ]

        for dimension, amount in checks:
            result = self.check(
                dimension,
                amount,
            )

            result.raise_if_exceeded()

        width = getattr(
            diagram,
            "width",
            None,
        )

        height = getattr(
            diagram,
            "height",
            None,
        )

        if (
            width is not None
            and height is not None
        ):
            self.validate_dimensions(
                float(width),
                float(height),
            )

    # ---------------------------------------------------------
    # State management
    # ---------------------------------------------------------

    def remaining(
        self,
    ) -> Dict[str, float]:
        return {
            "nodes": max(
                0,
                self.config.max_nodes
                - self.usage.nodes,
            ),
            "edges": max(
                0,
                self.config.max_edges
                - self.usage.edges,
            ),
            "groups": max(
                0,
                self.config.max_groups
                - self.usage.groups,
            ),
            "tokens": max(
                0,
                self.config.max_tokens
                - self.usage.tokens,
            ),
            "input_bytes": max(
                0,
                self.config.max_input_bytes
                - self.usage.input_bytes,
            ),
            "render_time_ms": max(
                0.0,
                self.config.max_render_time_ms
                - self.usage.render_time_ms,
            ),
            "operations": max(
                0,
                self.config.max_operations
                - self.usage.operations,
            ),
        }

    def utilization(
        self,
    ) -> Dict[str, float]:
        return {
            "nodes": self._ratio(
                self.usage.nodes,
                self.config.max_nodes,
            ),
            "edges": self._ratio(
                self.usage.edges,
                self.config.max_edges,
            ),
            "groups": self._ratio(
                self.usage.groups,
                self.config.max_groups,
            ),
            "tokens": self._ratio(
                self.usage.tokens,
                self.config.max_tokens,
            ),
            "input_bytes": self._ratio(
                self.usage.input_bytes,
                self.config.max_input_bytes,
            ),
            "render_time_ms": self._ratio(
                self.usage.render_time_ms,
                self.config.max_render_time_ms,
            ),
            "operations": self._ratio(
                self.usage.operations,
                self.config.max_operations,
            ),
        }

    def reset(self) -> None:
        self.usage = DiagramBudgetUsage()

    def snapshot(
        self,
    ) -> DiagramBudgetUsage:
        return self.usage.copy()

    def restore(
        self,
        snapshot: DiagramBudgetUsage,
    ) -> None:
        self.usage = snapshot.copy()

    def assert_within_limits(self) -> None:
        checks = [
            (
                BudgetDimension.NODES,
                self.usage.nodes,
            ),
            (
                BudgetDimension.EDGES,
                self.usage.edges,
            ),
            (
                BudgetDimension.GROUPS,
                self.usage.groups,
            ),
            (
                BudgetDimension.TOKENS,
                self.usage.tokens,
            ),
            (
                BudgetDimension.BYTES,
                self.usage.input_bytes,
            ),
            (
                BudgetDimension.RENDER_TIME,
                self.usage.render_time_ms,
            ),
            (
                BudgetDimension.OPERATIONS,
                self.usage.operations,
            ),
        ]

        for dimension, amount in checks:
            result = self.check(
                dimension,
                0,
            )

            if amount > result.limit:
                raise BudgetExceededError(
                    f"Budget exceeded for "
                    f"{dimension.value}: "
                    f"{amount} > {result.limit}"
                )

    # ---------------------------------------------------------
    # Internals
    # ---------------------------------------------------------

    def _values(
        self,
        dimension: BudgetDimension,
    ) -> tuple[float, float]:
        if dimension == BudgetDimension.NODES:
            return (
                self.usage.nodes,
                self.config.max_nodes,
            )

        if dimension == BudgetDimension.EDGES:
            return (
                self.usage.edges,
                self.config.max_edges,
            )

        if dimension == BudgetDimension.GROUPS:
            return (
                self.usage.groups,
                self.config.max_groups,
            )

        if dimension == BudgetDimension.TOKENS:
            return (
                self.usage.tokens,
                self.config.max_tokens,
            )

        if dimension == BudgetDimension.BYTES:
            return (
                self.usage.input_bytes,
                self.config.max_input_bytes,
            )

        if dimension == BudgetDimension.RENDER_TIME:
            return (
                self.usage.render_time_ms,
                self.config.max_render_time_ms,
            )

        if dimension == BudgetDimension.OPERATIONS:
            return (
                self.usage.operations,
                self.config.max_operations,
            )

        raise ValueError(
            f"Unknown budget dimension: {dimension}"
        )

    def _increment(
        self,
        dimension: BudgetDimension,
        amount: float,
    ) -> None:
        if dimension == BudgetDimension.NODES:
            self.usage.nodes += int(amount)

        elif dimension == BudgetDimension.EDGES:
            self.usage.edges += int(amount)

        elif dimension == BudgetDimension.GROUPS:
            self.usage.groups += int(amount)

        elif dimension == BudgetDimension.TOKENS:
            self.usage.tokens += int(amount)

        elif dimension == BudgetDimension.BYTES:
            self.usage.input_bytes += int(
                amount
            )

        elif dimension == BudgetDimension.RENDER_TIME:
            self.usage.render_time_ms += float(
                amount
            )

        elif dimension == BudgetDimension.OPERATIONS:
            self.usage.operations += int(
                amount
            )

        else:
            raise ValueError(
                f"Unknown budget dimension: {dimension}"
            )

    def _collection_length(
        self,
        value: Any,
    ) -> int:
        if value is None:
            return 0

        if isinstance(
            value,
            dict,
        ):
            return len(value)

        try:
            return len(value)
        except TypeError:
            return 0

    def _ratio(
        self,
        current: float,
        maximum: float,
    ) -> float:
        if maximum <= 0:
            return 1.0

        return min(
            1.0,
            current / maximum,
        )


def complexity_budget(node_count: int, edge_count: int) -> dict:
    """Return a small, deterministic complexity decision for agent tooling."""
    score = node_count * 0.8 + edge_count * 0.4
    if score < 20:
        level, action = "low", "single_canvas"
    elif score < 50:
        level, action = "medium", "single_canvas"
    elif score < 100:
        level, action = "high", "consider_split"
    else:
        level, action = "split", "split_into_subdiagrams"
    return {"level": level, "score": round(score, 2), "recommended_action": action}
