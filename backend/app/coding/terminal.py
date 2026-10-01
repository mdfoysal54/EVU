from __future__ import annotations

import os
import shlex
import subprocess
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Iterable, List, Optional


class TerminalError(Exception):
    """Terminal execution error."""


@dataclass
class CommandResult:
    command: List[str]

    returncode: int

    stdout: str = ""
    stderr: str = ""

    timed_out: bool = False

    @property
    def success(self) -> bool:
        return (
            self.returncode == 0
            and not self.timed_out
        )

    @property
    def output(self) -> str:
        if self.stderr:
            return (
                self.stdout
                + "\n"
                + self.stderr
            )

        return self.stdout


@dataclass
class Terminal:
    """
    Controlled command executor.

    Commands are executed without shell interpretation by default.
    """

    cwd: Path

    timeout: float = 60.0

    allowed_commands: Optional[
        Iterable[str]
    ] = None

    environment: Dict[str, str] = field(
        default_factory=dict
    )

    def __post_init__(self) -> None:
        self.cwd = Path(
            self.cwd
        ).resolve()

        if self.allowed_commands is None:
            self.allowed_commands = {
                "python",
                "python3",
                "pytest",
                "git",
                "pip",
                "pip3",
                "ruff",
                "mypy",
                "node",
                "npm",
            }

        self.allowed_commands = {
            command.lower()
            for command in self.allowed_commands
        }

    def _normalize(
        self,
        command: str | List[str],
    ) -> List[str]:

        if isinstance(command, str):
            if os.name == "nt":
                parts = shlex.split(
                    command,
                    posix=False,
                )
            else:
                parts = shlex.split(
                    command
                )
        else:
            parts = list(command)

        if not parts:
            raise TerminalError(
                "Empty command."
            )

        return parts

    def _validate_command(
        self,
        parts: List[str],
    ) -> None:

        executable = Path(
            parts[0]
        ).name.lower()

        if executable not in (
            self.allowed_commands
            or set()
        ):
            raise TerminalError(
                f"Command is not allowed: "
                f"{executable}"
            )

    def run(
        self,
        command: str | List[str],
        *,
        timeout: Optional[float] = None,
    ) -> CommandResult:

        parts = self._normalize(
            command
        )

        self._validate_command(
            parts
        )

        environment = os.environ.copy()
        environment.update(
            self.environment
        )

        try:

            completed = subprocess.run(
                parts,
                cwd=self.cwd,
                env=environment,
                capture_output=True,
                text=True,
                timeout=(
                    timeout
                    if timeout is not None
                    else self.timeout
                ),
                shell=False,
            )

            return CommandResult(
                command=parts,
                returncode=(
                    completed.returncode
                ),
                stdout=completed.stdout,
                stderr=completed.stderr,
            )

        except subprocess.TimeoutExpired as exc:

            return CommandResult(
                command=parts,
                returncode=-1,
                stdout=(
                    exc.stdout
                    if isinstance(
                        exc.stdout,
                        str,
                    )
                    else ""
                ),
                stderr=(
                    exc.stderr
                    if isinstance(
                        exc.stderr,
                        str,
                    )
                    else "Command timed out."
                ),
                timed_out=True,
            )