from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, Dict, List, Optional

from .context import PipelineContext


Condition = Callable[[PipelineContext], bool]


@dataclass
class Branch:
    name: str
    condition: Condition
    stage_names: List[str] = field(default_factory=list)


@dataclass
class BranchRouter:
    """
    Selects a branch according to context.

    First matching branch wins unless `allow_multiple=True`.
    """

    branches: List[Branch] = field(default_factory=list)
    default_branch: Optional[str] = None
    allow_multiple: bool = False

    def add(
        self,
        name: str,
        condition: Condition,
        stage_names: Optional[List[str]] = None,
    ) -> "BranchRouter":

        self.branches.append(
            Branch(
                name=name,
                condition=condition,
                stage_names=stage_names or [],
            )
        )

        return self

    def select(self, context: PipelineContext) -> List[Branch]:
        matches = [
            branch
            for branch in self.branches
            if branch.condition(context)
        ]

        if self.allow_multiple:
            return matches

        if matches:
            return [matches[0]]

        if self.default_branch:
            for branch in self.branches:
                if branch.name == self.default_branch:
                    return [branch]

        return []

    def selected_stage_names(
        self,
        context: PipelineContext,
    ) -> List[str]:

        selected = self.select(context)

        result: List[str] = []

        for branch in selected:
            result.extend(branch.stage_names)

        return result