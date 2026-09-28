from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional


class NodeType(str, Enum):
    TASK = "task"
    PIPELINE = "pipeline"
    CONDITION = "condition"
    PARALLEL = "parallel"
    LOOP = "loop"
    START = "start"
    END = "end"


class NodeStatus(str, Enum):
    PENDING = "pending"
    READY = "ready"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    SKIPPED = "skipped"
    CANCELLED = "cancelled"


@dataclass
class NodeSpec:
    id: str
    name: str

    node_type: NodeType = NodeType.TASK

    handler: Any = None

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )

    retry: Optional[Dict[str, Any]] = None


@dataclass
class EdgeSpec:
    source: str
    target: str

    condition: Any = None

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )


@dataclass
class WorkflowDefinition:
    id: str
    name: str

    nodes: List[NodeSpec] = field(
        default_factory=list
    )

    edges: List[EdgeSpec] = field(
        default_factory=list
    )

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )

    max_iterations: int = 100

    def node_ids(self) -> List[str]:
        return [node.id for node in self.nodes]