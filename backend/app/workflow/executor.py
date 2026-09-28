from __future__ import annotations

import asyncio
from dataclasses import dataclass, field
from typing import Any, Dict, Optional
from uuid import uuid4

from .checkpoints import (
    WorkflowCheckpointStore,
)
from .evaluator import ConditionEvaluator
from .graph import WorkflowGraph
from .models import (
    NodeStatus,
    WorkflowDefinition,
)
from .nodes import create_node_executor
from .parallel import ParallelExecutor
from .state import WorkflowState
from .variables import VariableStore


@dataclass
class WorkflowResult:
    success: bool
    workflow_id: str
    execution_id: str

    state: WorkflowState

    error: Optional[str] = None

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )


class WorkflowExecutor:
    """
    Main Workflow DAG execution engine.

    Responsibilities:

    - validate DAG
    - determine ready nodes
    - evaluate edge conditions
    - execute independent nodes
    - update workflow state
    - checkpoint execution
    - support async handlers
    """

    def __init__(
        self,
        checkpoint_store: Optional[
            WorkflowCheckpointStore
        ] = None,
        parallel_executor: Optional[
            ParallelExecutor
        ] = None,
    ) -> None:

        self.checkpoints = (
            checkpoint_store
            or WorkflowCheckpointStore()
        )

        self.parallel = (
            parallel_executor
            or ParallelExecutor()
        )

    def _build_graph(
        self,
        definition: WorkflowDefinition,
    ) -> WorkflowGraph:

        return WorkflowGraph(
            definition.nodes,
            definition.edges,
        )

    def _ready_nodes(
        self,
        graph: WorkflowGraph,
        state: WorkflowState,
        evaluator: ConditionEvaluator,
    ) -> list[str]:

        ready = []

        for node_id in graph.nodes:

            node_state = state.node(
                node_id
            )

            if node_state.status != NodeStatus.PENDING:
                continue

            incoming = graph.incoming(
                node_id
            )

            if not incoming:
                ready.append(node_id)
                continue

            enabled = evaluator.select_edges(
                incoming
            )

            # A node becomes reachable when at least one
            # enabled predecessor has completed.
            if not enabled:
                state.mark_skipped(
                    node_id
                )
                continue

            if all(
                state.node(edge.source).status
                in {
                    NodeStatus.SUCCESS,
                    NodeStatus.SKIPPED,
                }
                for edge in enabled
            ):
                ready.append(node_id)

        return ready

    async def _execute_node(
        self,
        node_id: str,
        graph: WorkflowGraph,
        state: WorkflowState,
        variables: VariableStore,
    ) -> None:

        node = graph.nodes[node_id]

        state.mark_running(node_id)

        try:
            executor = create_node_executor(
                node.node_type
            )

            result = await executor.execute(
                node,
                state,
                variables,
            )

            state.mark_success(
                node_id,
                result,
            )

            # Make node result available to later nodes.
            variables.set(
                f"nodes.{node_id}.result",
                result,
            )

            variables.set(
                f"nodes.{node_id}.status",
                "success",
            )

        except Exception as exc:

            state.mark_failed(
                node_id,
                str(exc),
            )

            variables.set(
                f"nodes.{node_id}.status",
                "failed",
            )

            raise

    async def execute(
        self,
        definition: WorkflowDefinition,
        *,
        variables: Optional[
            Dict[str, Any]
        ] = None,
        execution_id: Optional[str] = None,
        checkpoint: bool = True,
        fail_fast: bool = True,
    ) -> WorkflowResult:

        graph = self._build_graph(
            definition
        )

        execution_id = (
            execution_id
            or str(uuid4())
        )

        variable_store = VariableStore(
            variables or {}
        )

        state = WorkflowState(
            workflow_id=definition.id,
            execution_id=execution_id,
            variables=variable_store.all(),
        )

        evaluator = ConditionEvaluator(
            variable_store
        )

        try:

            while True:

                if state.cancelled:
                    return WorkflowResult(
                        success=False,
                        workflow_id=definition.id,
                        execution_id=execution_id,
                        state=state,
                        error="Workflow cancelled.",
                    )

                if state.is_complete():
                    break

                ready = self._ready_nodes(
                    graph,
                    state,
                    evaluator,
                )

                if not ready:

                    unresolved = [
                        node_id
                        for node_id in graph.nodes
                        if state.node(
                            node_id
                        ).status
                        == NodeStatus.PENDING
                    ]

                    if unresolved:
                        raise RuntimeError(
                            "Workflow cannot make progress. "
                            f"Unresolved nodes: {unresolved}"
                        )

                    break

                async def make_task(
                    node_id: str,
                ) -> Any:

                    return await self._execute_node(
                        node_id,
                        graph,
                        state,
                        variable_store,
                    )

                if len(ready) == 1:
                    await make_task(
                        ready[0]
                    )

                else:

                    result = await self.parallel.run(
                        [
                            lambda node_id=node_id:
                            make_task(node_id)
                            for node_id in ready
                        ],
                        fail_fast=fail_fast,
                    )

                    if result.errors and fail_fast:
                        raise result.errors[0]

                state.variables = (
                    variable_store.all()
                )

                if checkpoint:
                    self.checkpoints.save(
                        checkpoint_id=(
                            f"{execution_id}:"
                            f"{len(state.nodes)}"
                        ),
                        workflow_id=definition.id,
                        execution_id=execution_id,
                        state=state.snapshot(),
                    )

            state.finished_at = (
                __import__(
                    "datetime"
                ).datetime.now(
                    __import__(
                        "datetime"
                    ).timezone.utc
                )
            )

            return WorkflowResult(
                success=True,
                workflow_id=definition.id,
                execution_id=execution_id,
                state=state,
            )

        except Exception as exc:

            state.finished_at = (
                __import__(
                    "datetime"
                ).datetime.now(
                    __import__(
                        "datetime"
                    ).timezone.utc
                )
            )

            return WorkflowResult(
                success=False,
                workflow_id=definition.id,
                execution_id=execution_id,
                state=state,
                error=str(exc),
            )

    def execute_sync(
        self,
        definition: WorkflowDefinition,
        **kwargs: Any,
    ) -> WorkflowResult:

        return asyncio.run(
            self.execute(
                definition,
                **kwargs,
            )
        )