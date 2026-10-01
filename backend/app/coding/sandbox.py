from __future__ import annotations

import os
import shutil
import subprocess
import tempfile
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional


class SandboxError(Exception):
    """Sandbox operation failed."""


@dataclass
class SandboxConfig:
    timeout: float = 30.0

    memory_limit_mb: Optional[int] = None

    environment: Dict[str, str] = field(
        default_factory=dict
    )

    allowed_commands: Optional[
        List[str]
    ] = None

    network_enabled: bool = False


@dataclass
class SandboxResult:
    success: bool

    command: List[str]

    returncode: int

    stdout: str = ""
    stderr: str = ""

    timed_out: bool = False

    duration_seconds: float = 0.0

    workspace: Optional[str] = None


class Sandbox:
    """
    Process-isolation boundary for coding experiments.

    Important:
        This is a lightweight local sandbox, not a security-grade
        container/VM. Production untrusted-code execution should
        eventually move to a container/VM isolation layer.
    """

    def __init__(
        self,
        config: Optional[
            SandboxConfig
        ] = None,
    ) -> None:

        self.config = (
            config
            or SandboxConfig()
        )

    def _validate_command(
        self,
        command: List[str],
    ) -> None:

        if not command:
            raise SandboxError(
                "Empty command."
            )

        if (
            self.config.allowed_commands
            is None
        ):
            return

        executable = Path(
            command[0]
        ).name.lower()

        allowed = {
            Path(item).name.lower()
            for item in
            self.config.allowed_commands
        }

        if executable not in allowed:
            raise SandboxError(
                f"Command is not allowed: "
                f"{executable}"
            )

    def run(
        self,
        command: List[str],
        *,
        workspace: Optional[
            str | Path
        ] = None,
        timeout: Optional[
            float
        ] = None,
    ) -> SandboxResult:

        self._validate_command(
            command
        )

        temporary = (
            workspace is None
        )

        if temporary:

            directory = Path(
                tempfile.mkdtemp(
                    prefix="evu-sandbox-"
                )
            )

        else:

            directory = Path(
                workspace
            ).resolve()

            directory.mkdir(
                parents=True,
                exist_ok=True,
            )

        environment = os.environ.copy()

        environment.update(
            self.config.environment
        )

        started = time.monotonic()

        try:

            completed = subprocess.run(
                command,
                cwd=directory,
                env=environment,
                capture_output=True,
                text=True,
                timeout=(
                    timeout
                    if timeout is not None
                    else self.config.timeout
                ),
                shell=False,
            )

            return SandboxResult(
                success=(
                    completed.returncode == 0
                ),
                command=command,
                returncode=(
                    completed.returncode
                ),
                stdout=completed.stdout,
                stderr=completed.stderr,
                duration_seconds=(
                    time.monotonic()
                    - started
                ),
                workspace=str(
                    directory
                ),
            )

        except subprocess.TimeoutExpired as exc:

            return SandboxResult(
                success=False,
                command=command,
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
                    else "Sandbox execution timed out."
                ),
                timed_out=True,
                duration_seconds=(
                    time.monotonic()
                    - started
                ),
                workspace=str(
                    directory
                ),
            )

        finally:

            if temporary:

                shutil.rmtree(
                    directory,
                    ignore_errors=True,
                )