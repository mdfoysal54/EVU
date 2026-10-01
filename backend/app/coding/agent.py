from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from app.experience import (
    EventType,
    ExperienceRecorder,
    ExperienceService,
    ExperienceStatus,
)

from .debugger import Debugger
from .filesystem import WorkspaceFilesystem
from .git import GitRepository
from .patch import PatchManager
from .planner import CodingPlan, CodingPlanner
from .sandbox import Sandbox
from .terminal import Terminal
from .test_runner import TestResult, TestRunner
from .verifier import VerificationResult, Verifier
from .workspace import Workspace


@dataclass
class CodingAgentResult:
    success: bool
    task: str
    plan: Optional[CodingPlan] = None
    test_result: Optional[TestResult] = None
    verification: Optional[VerificationResult] = None
    changed_files: List[str] = field(default_factory=list)
    error: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


class CodingAgent:
    """EVU Coding Agent orchestration layer.

    Intelligence is intentionally injected instead of hard-coded.

    The Agent coordinates:
        Planner
        Workspace
        Filesystem
        Terminal
        Git
        PatchManager
        TestRunner
        Debugger
        Sandbox
        Verifier
        ExperienceService
    """

    def __init__(
        self,
        workspace: Workspace,
        *,
        planner: Optional[CodingPlanner] = None,
        experience_service: Optional[ExperienceService] = None,
        sandbox: Optional[Sandbox] = None,
    ) -> None:
        self.workspace = workspace
        self.filesystem: WorkspaceFilesystem = workspace.filesystem
        self.terminal = Terminal(workspace.root)
        self.git = GitRepository(workspace.root)
        self.patch = PatchManager(self.filesystem)
        self.tests = TestRunner(workspace.root, terminal=self.terminal)
        self.debugger = Debugger()
        self.sandbox = sandbox or Sandbox()
        self.verifier = Verifier()
        self.planner = planner or CodingPlanner()
        self.experience_service = experience_service

    async def plan(self, task: str) -> CodingPlan:
        return await self.planner.create(task)

    def inspect_workspace(self) -> List[str]:
        return self.filesystem.list(".", recursive=True)

    def apply_file(self, path: str, content: str):
        return self.patch.replace_file(path, content)

    def run_command(
        self,
        command: str | List[str],
        *,
        timeout: Optional[float] = None,
    ):
        return self.terminal.run(command, timeout=timeout)

    def run_tests(
        self,
        *,
        path: str = ".",
        timeout: Optional[float] = None,
    ) -> TestResult:
        return self.tests.run(path=path, timeout=timeout)

    def verify(
        self,
        test_result: Optional[TestResult] = None,
        required_files: Optional[List[str]] = None,
    ) -> VerificationResult:
        checks = []

        if test_result is not None:
            checks.append(self.verifier.verify_tests(test_result))

        if required_files:
            checks.append(
                self.verifier.verify_files(
                    self.filesystem,
                    required_files,
                )
            )

        return self.verifier.verify(checks)

    async def execute(
        self,
        task: str,
        *,
        run_tests: bool = True,
        test_path: str = ".",
        required_files: Optional[List[str]] = None,
    ) -> CodingAgentResult:
        recorder: Optional[ExperienceRecorder] = None

        if self.experience_service:
            recorder = self.experience_service.start(
                task,
                agent_id="evu-coding-agent",
                metadata={"workspace": str(self.workspace.root)},
            )

        try:
            plan = await self.plan(task)

            if recorder:
                recorder.record(
                    EventType.ACTION,
                    name="coding.plan",
                    payload={
                        "steps": [
                            {
                                "id": step.id,
                                "title": step.title,
                                "action": step.action,
                            }
                            for step in plan.steps
                        ]
                    },
                )

            files = self.inspect_workspace()

            if recorder:
                recorder.observe(
                    {"workspace_files": files},
                    name="workspace.inspect",
                )

            test_result = None

            if run_tests:
                test_result = self.run_tests(path=test_path)

                if recorder:
                    recorder.record(
                        EventType.TOOL_RESULT,
                        name="test_runner",
                        output_data={
                            "success": test_result.success,
                            "returncode": test_result.returncode,
                            "stdout": test_result.stdout,
                            "stderr": test_result.stderr,
                        },
                    )

            verification = self.verify(test_result, required_files)

            if recorder:
                recorder.verify(
                    verification.summary,
                    name="coding.verification",
                    metadata={"success": verification.success},
                )

            success = verification.success

            if not run_tests and not required_files:
                success = True

            if recorder:
                self.experience_service.finish_and_save(
                    recorder,
                    (
                        ExperienceStatus.SUCCESS
                        if success
                        else ExperienceStatus.FAILED
                    ),
                    output_data={
                        "success": success,
                        "verification": verification.summary,
                    },
                )

            return CodingAgentResult(
                success=success,
                task=task,
                plan=plan,
                test_result=test_result,
                verification=verification,
                metadata={"workspace": str(self.workspace.root)},
            )

        except Exception as exc:
            if recorder:
                recorder.error(
                    str(exc),
                    metadata={"component": "coding_agent"},
                )
                self.experience_service.finish_and_save(
                    recorder,
                    ExperienceStatus.FAILED,
                    output_data={"error": str(exc)},
                )

            return CodingAgentResult(
                success=False,
                task=task,
                error=str(exc),
                metadata={"workspace": str(self.workspace.root)},
            )