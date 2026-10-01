from __future__ import annotations

import shutil
from pathlib import Path
from typing import Iterable, List


class FilesystemError(Exception):
    """Filesystem operation failed."""


class WorkspaceFilesystem:
    """
    Filesystem abstraction restricted to one workspace root.

    All paths are resolved and checked before use.
    """

    def __init__(
        self,
        root: str | Path,
    ) -> None:

        self.root = Path(root).resolve()
        self.root.mkdir(
            parents=True,
            exist_ok=True,
        )

    def resolve(
        self,
        path: str | Path,
    ) -> Path:

        candidate = Path(path)

        if not candidate.is_absolute():
            candidate = self.root / candidate

        resolved = candidate.resolve()

        try:
            resolved.relative_to(
                self.root
            )
        except ValueError as exc:
            raise FilesystemError(
                f"Path escapes workspace: {path}"
            ) from exc

        return resolved

    def exists(
        self,
        path: str | Path,
    ) -> bool:

        return self.resolve(path).exists()

    def is_file(
        self,
        path: str | Path,
    ) -> bool:

        return self.resolve(path).is_file()

    def is_dir(
        self,
        path: str | Path,
    ) -> bool:

        return self.resolve(path).is_dir()

    def read(
        self,
        path: str | Path,
        *,
        encoding: str = "utf-8",
    ) -> str:

        target = self.resolve(path)

        if not target.is_file():
            raise FilesystemError(
                f"File does not exist: {path}"
            )

        return target.read_text(
            encoding=encoding
        )

    def write(
        self,
        path: str | Path,
        content: str,
        *,
        encoding: str = "utf-8",
    ) -> Path:

        target = self.resolve(path)

        target.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        target.write_text(
            content,
            encoding=encoding,
        )

        return target

    def append(
        self,
        path: str | Path,
        content: str,
        *,
        encoding: str = "utf-8",
    ) -> Path:

        target = self.resolve(path)

        target.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        with target.open(
            "a",
            encoding=encoding,
        ) as file:

            file.write(content)

        return target

    def mkdir(
        self,
        path: str | Path,
    ) -> Path:

        target = self.resolve(path)

        target.mkdir(
            parents=True,
            exist_ok=True,
        )

        return target

    def delete(
        self,
        path: str | Path,
    ) -> None:

        target = self.resolve(path)

        if target == self.root:
            raise FilesystemError(
                "Cannot delete workspace root."
            )

        if target.is_dir():
            shutil.rmtree(target)

        elif target.exists():
            target.unlink()

    def copy(
        self,
        source: str | Path,
        destination: str | Path,
    ) -> Path:

        source_path = self.resolve(source)
        destination_path = self.resolve(
            destination
        )

        if not source_path.exists():
            raise FilesystemError(
                f"Source does not exist: {source}"
            )

        destination_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        if source_path.is_dir():
            shutil.copytree(
                source_path,
                destination_path,
                dirs_exist_ok=True,
            )
        else:
            shutil.copy2(
                source_path,
                destination_path,
            )

        return destination_path

    def list(
        self,
        path: str | Path = ".",
        *,
        recursive: bool = False,
    ) -> List[str]:

        target = self.resolve(path)

        if not target.is_dir():
            raise FilesystemError(
                f"Not a directory: {path}"
            )

        iterator: Iterable[Path]

        if recursive:
            iterator = target.rglob("*")
        else:
            iterator = target.iterdir()

        return [
            str(item.relative_to(self.root))
            for item in iterator
        ]

    def find_files(
        self,
        pattern: str = "*",
    ) -> List[str]:

        return [
            str(
                path.relative_to(
                    self.root
                )
            )
            for path in self.root.rglob(
                pattern
            )
            if path.is_file()
        ]