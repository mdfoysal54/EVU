from __future__ import annotations

import inspect
from dataclasses import dataclass
from typing import Any, Awaitable, Callable, Optional

from .models import NodeSpec, NodeType
from .state import WorkflowState
from .variables import VariableStore


@dataclass
class NodeContext:
    node: NodeSpec
    state: WorkflowState
    variables: VariableStore

    def get(
        self,
        key: str,
        default: Any = None,
    ) -> Any:

        return self.variables.get(
            key,
            default,
        )

    def set(
        self,
        key: str,
        value: Any,
    ) -> None:

        self.variables.set(
            key,
            value,
        )


class NodeExecutor:
    """
    Executes an individual workflow node.

    `handler` may be:

        handler(context)

    and may return either a normal result or an awaitable.
    """

    async def execute(
        self,
        node: NodeSpec,
        state: WorkflowState,
        variables: VariableStore,
    ) -> Any:

        context = NodeContext(
            node=node,
            state=state,
            variables=variables,
        )

        if node.handler is None:
            return None

        result = node.handler(context)

        if inspect.isawaitable(result):
            return await result

        return result


class TaskNode(NodeExecutor):
    pass


class PipelineNode(NodeExecutor):
    """
    Pipeline-compatible workflow node.

    The handler can be a PipelineRunner wrapper or any callable
    returning a pipeline result.
    """

    async def execute(
        self,
        node: NodeSpec,
        state: WorkflowState,
        variables: VariableStore,
    ) -> Any:

        return await super().execute(
            node,
            state,
            variables,
        )


class ConditionNode(NodeExecutor):
    pass


def create_node_executor(
    node_type: NodeType,
) -> NodeExecutor:

    if node_type == NodeType.PIPELINE:
        return PipelineNode()

    if node_type == NodeType.CONDITION:
        return ConditionNode()

    return TaskNode()