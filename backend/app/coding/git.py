from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional

from .terminal import CommandResult, Terminal


class GitError(Exception):
    """Git operation failed."""


@dataclass
class GitRepository:
    """
    Controlled Git interface for a coding workspace.
    """

    root: Path
    terminal: Optional[Terminal] = None

    def __post_init__(self) -> None:
        self.root = Path(
            self.root
        ).resolve()

        self.terminal = (
            self.terminal
            or Terminal(
                self.root,
                allowed_commands={"git"},
            )
        )

    def run(
        self,
        args: List[str],
    ) -> CommandResult:

        result = self.terminal.run(
            ["git", *args]
        )

        if not result.success:
            raise GitError(
                result.stderr
                or result.stdout
                or "Git command failed."
            )

        return result

    def is_repository(self) -> bool:

        result = self.terminal.run(
            [
                "git",
                "rev-parse",
                "--is-inside-work-tree",
            ]
        )

        return (
            result.success
            and result.stdout.strip()
            == "true"
        )

    def status(
        self,
    ) -> CommandResult:

        return self.run(
            [
                "status",
                "--short",
            ]
        )

    def diff(
        self,
        *,
        staged: bool = False,
    ) -> str:

        args = ["diff"]

        if staged:
            args.append("--cached")

        result = self.run(args)

        return result.stdout

    def branch(
        self,
    ) -> str:

        result = self.run(
            [
                "branch",
                "--show-current",
            ]
        )

        return result.stdout.strip()

    def log(
        self,
        limit: int = 10,
    ) -> str:

        result = self.run(
            [
                "log",
                f"-{limit}",
                "--oneline",
            ]
        )

        return result.stdout

    def init(self) -> CommandResult:

        return self.run(["init"])

    def add(
        self,
        paths: List[str],
    ) -> CommandResult:

        if not paths:
            raise GitError(
                "No paths provided."
            )

        return self.run(
            ["add", "--", *paths]
        )

    def commit(
        self,
        message: str,
    ) -> CommandResult:

        if not message.strip():
            raise GitError(
                "Commit message cannot be empty."
            )

        return self.run(
            [
                "commit",
                "-m",
                message,
            ]
        )

    def checkout(
        self,
        branch: str,
    ) -> CommandResult:

        if not branch.strip():
            raise GitError(
                "Branch cannot be empty."
            )

        return self.run(
            [
                "checkout",
                branch,
            ]
        )