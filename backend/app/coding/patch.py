from __future__ import annotations

import difflib
import re
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional, Tuple

from .filesystem import WorkspaceFilesystem


class PatchError(Exception):
    """Patch operation failed."""


@dataclass
class PatchResult:
    success: bool

    files_changed: List[str]

    additions: int = 0
    deletions: int = 0

    error: Optional[str] = None


class PatchManager:
    """
    Safe patch manager.

    Supports:
      1. replacing a complete file
      2. applying unified diffs
      3. generating diffs

    All target paths are restricted to the workspace.
    """

    HUNK_RE = re.compile(
        r"^@@ -(\d+)(?:,(\d+))? "
        r"\+(\d+)(?:,(\d+))? @@"
    )

    def __init__(
        self,
        filesystem: WorkspaceFilesystem,
    ) -> None:

        self.filesystem = filesystem

    def replace_file(
        self,
        path: str,
        content: str,
    ) -> PatchResult:

        try:
            self.filesystem.write(
                path,
                content,
            )

            return PatchResult(
                success=True,
                files_changed=[path],
                additions=len(
                    content.splitlines()
                ),
            )

        except Exception as exc:

            return PatchResult(
                success=False,
                files_changed=[],
                error=str(exc),
            )

    def diff(
        self,
        path: str,
        old: str,
        new: str,
    ) -> str:

        return "".join(
            difflib.unified_diff(
                old.splitlines(
                    keepends=True
                ),
                new.splitlines(
                    keepends=True
                ),
                fromfile=path,
                tofile=path,
            )
        )

    def apply_unified_diff(
        self,
        patch: str,
    ) -> PatchResult:

        if not patch.strip():
            return PatchResult(
                success=True,
                files_changed=[],
            )

        lines = patch.splitlines(
            keepends=True
        )

        current_file: Optional[str] = None

        output: List[str] = []

        index = 0

        additions = 0
        deletions = 0

        changed_files: List[str] = []

        try:

            while index < len(lines):

                line = lines[index]

                if line.startswith(
                    "+++ "
                ):
                    current_file = (
                        line[4:]
                        .strip()
                    )

                    if current_file.startswith(
                        "b/"
                    ):
                        current_file = (
                            current_file[2:]
                        )

                    changed_files.append(
                        current_file
                    )

                    index += 1
                    continue

                if line.startswith(
                    "--- "
                ):
                    index += 1
                    continue

                if line.startswith(
                    "@@ "
                ):
                    if current_file is None:
                        raise PatchError(
                            "Hunk has no target file."
                        )

                    original = self.filesystem.read(
                        current_file
                    ).splitlines(
                        keepends=True
                    )

                    match = self.HUNK_RE.match(
                        line
                    )

                    if not match:
                        raise PatchError(
                            f"Invalid hunk header: "
                            f"{line.strip()}"
                        )

                    old_start = int(
                        match.group(1)
                    )

                    old_count = int(
                        match.group(2)
                        or "1"
                    )

                    new_start = int(
                        match.group(3)
                    )

                    new_count = int(
                        match.group(4)
                        or "1"
                    )

                    # Keep original content outside the hunk.
                    prefix = original[
                        : old_start - 1
                    ]

                    suffix_start = (
                        old_start
                        - 1
                        + old_count
                    )

                    suffix = original[
                        suffix_start:
                    ]

                    hunk_output: List[
                        str
                    ] = []

                    index += 1

                    consumed_old = 0

                    while (
                        index < len(lines)
                    ):

                        hunk_line = lines[
                            index
                        ]

                        if (
                            hunk_line.startswith(
                                "@@ "
                            )
                            or hunk_line.startswith(
                                "--- "
                            )
                            or hunk_line.startswith(
                                "+++ "
                            )
                        ):
                            break

                        if (
                            hunk_line
                            == "\\ No newline at end of file\n"
                        ):
                            index += 1
                            continue

                        marker = (
                            hunk_line[:1]
                        )

                        content = (
                            hunk_line[1:]
                        )

                        if marker == " ":
                            hunk_output.append(
                                content
                            )
                            consumed_old += 1

                        elif marker == "-":
                            consumed_old += 1
                            deletions += 1

                        elif marker == "+":
                            hunk_output.append(
                                content
                            )
                            additions += 1

                        else:
                            break

                        index += 1

                    if (
                        consumed_old
                        != old_count
                    ):
                        raise PatchError(
                            "Patch hunk does not "
                            "match expected source "
                            "line count."
                        )

                    new_content = (
                        prefix
                        + hunk_output
                        + suffix
                    )

                    self.filesystem.write(
                        current_file,
                        "".join(new_content),
                    )

                    continue

                index += 1

            return PatchResult(
                success=True,
                files_changed=list(
                    dict.fromkeys(
                        changed_files
                    )
                ),
                additions=additions,
                deletions=deletions,
            )

        except Exception as exc:

            return PatchResult(
                success=False,
                files_changed=changed_files,
                additions=additions,
                deletions=deletions,
                error=str(exc),
            )