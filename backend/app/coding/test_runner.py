from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional

from .terminal import CommandResult, Terminal


@dataclass
class TestResult:
    success: bool

    command: List[str]

    returncode: int

    stdout: str = ""
    stderr: str = ""

    timed_out: bool = False

    duration_seconds: Optional[
        float
    ] = None

    failed_tests: List[str] = field(
        default_factory=list
    )

    @property
    def output(self) -> str:
        return (
            self.stdout
            + (
                "\n" + self.stderr
                if self.stderr
                else ""
            )
        )


class TestRunner:
    """
    Test execution abstraction.

    Default command is pytest, but EVU can provide another runner.
    """

    def __init__(
        self,
        root: str | Path,
        terminal: Optional[
            Terminal
        ] = None,
    ) -> None:

        self.root = Path(root).resolve()

        self.terminal = (
            terminal
            or Terminal(
                self.root
            )
        )

    def run(
        self,
        *,
        path: str = ".",
        command: Optional[
            List[str]
        ] = None,
        timeout: Optional[
            float
        ] = None,
    ) -> TestResult:

        import time

        if command is None:
            command = [
                "pytest",
                path,
                "-q",
            ]

        started = time.monotonic()

        result = self.terminal.run(
            command,
            timeout=timeout,
        )

        duration = (
            time.monotonic()
            - started
        )

        return TestResult(
            success=result.success,
            command=result.command,
            returncode=result.returncode,
            stdout=result.stdout,
            stderr=result.stderr,
            timed_out=result.timed_out,
            duration_seconds=duration,
            failed_tests=self._extract_failures(
                result
            ),
        )

    def _extract_failures(
        self,
        result: CommandResult,
    ) -> List[str]:

        failures = []

        for line in result.stdout.splitlines():

            if (
                "FAILED " in line
                or line.startswith("FAILED")
            ):
                failures.append(
                    line.strip()
                )

        return failures