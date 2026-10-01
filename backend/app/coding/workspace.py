from __future__ import annotations

import tempfile
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Optional

from .filesystem import WorkspaceFilesystem


@dataclass
class Workspace:
    """
    Coding-agent workspace.

    The workspace owns the filesystem boundary used by coding tools.
    """

    root: Path

    metadata: Dict[str, str] = field(
        default_factory=dict
    )

    persistent: bool = True

    def __post_init__(self) -> None:
        self.root = Path(
            self.root
        ).resolve()

        self.root.mkdir(
            parents=True,
            exist_ok=True,
        )

        self.filesystem = (
            WorkspaceFilesystem(
                self.root
            )
        )

    @classmethod
    def create(
        cls,
        root: Optional[str | Path] = None,
        *,
        prefix: str = "evu-coding-",
        persistent: bool = True,
    ) -> "Workspace":

        if root is not None:
            return cls(
                Path(root),
                persistent=persistent,
            )

        directory = tempfile.mkdtemp(
            prefix=prefix
        )

        return cls(
            Path(directory),
            persistent=False,
        )

    def path(
        self,
        relative: str | Path = ".",
    ) -> Path:

        return self.filesystem.resolve(
            relative
        )

    def read(
        self,
        path: str | Path,
    ) -> str:

        return self.filesystem.read(path)

    def write(
        self,
        path: str | Path,
        content: str,
    ) -> Path:

        return self.filesystem.write(
            path,
            content,
        )

    def snapshot(self) -> Dict[str, object]:

        return {
            "root": str(self.root),
            "persistent": self.persistent,
            "metadata": dict(
                self.metadata
            ),
        }