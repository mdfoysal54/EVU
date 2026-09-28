from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable, List, Optional, Set


@dataclass
class SourceFile:
    path: Path
    relative_path: str
    extension: str
    size: int
    lines: int


@dataclass
class CodebaseScanner:
    root: Path | str

    include_extensions: Set[str] = field(
        default_factory=lambda: {
            ".py",
            ".js",
            ".jsx",
            ".ts",
            ".tsx",
            ".json",
            ".yaml",
            ".yml",
        }
    )

    ignored_directories: Set[str] = field(
        default_factory=lambda: {
            ".git",
            ".venv",
            "venv",
            "__pycache__",
            "node_modules",
            ".next",
            "dist",
            "build",
            ".pytest_cache",
        }
    )

    def __post_init__(self) -> None:
        self.root = Path(self.root).resolve()

    def scan(self) -> List[SourceFile]:
        results: list[SourceFile] = []

        if not self.root.exists():
            raise FileNotFoundError(
                f"Codebase root does not exist: {self.root}"
            )

        for path in self.root.rglob("*"):
            if not path.is_file():
                continue

            if any(
                part in self.ignored_directories
                for part in path.parts
            ):
                continue

            if path.suffix.lower() not in self.include_extensions:
                continue

            try:
                text = path.read_text(
                    encoding="utf-8"
                )

                lines = len(
                    text.splitlines()
                )

            except (UnicodeDecodeError, OSError):
                continue

            relative = path.relative_to(
                self.root
            )

            results.append(
                SourceFile(
                    path=path,
                    relative_path=str(relative),
                    extension=path.suffix.lower(),
                    size=path.stat().st_size,
                    lines=lines,
                )
            )

        return sorted(
            results,
            key=lambda item: item.relative_path.lower(),
        )

    def find(
        self,
        pattern: str,
    ) -> List[SourceFile]:
        pattern = pattern.lower()

        return [
            item
            for item in self.scan()
            if pattern in item.relative_path.lower()
        ]