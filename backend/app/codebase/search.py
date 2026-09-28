from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import List

from .indexer import CodebaseIndex


@dataclass
class SearchResult:
    file: str
    line: int
    text: str
    score: float = 0.0


class CodeSearch:
    def __init__(
        self,
        root: Path | str,
        index: CodebaseIndex | None = None,
    ) -> None:
        self.root = Path(root).resolve()
        self.index = index

    def text(
        self,
        query: str,
        case_sensitive: bool = False,
    ) -> List[SearchResult]:
        results: list[SearchResult] = []

        needle = (
            query
            if case_sensitive
            else query.lower()
        )

        for path in self.root.rglob("*"):
            if not path.is_file():
                continue

            if path.suffix.lower() not in {
                ".py",
                ".js",
                ".jsx",
                ".ts",
                ".tsx",
            }:
                continue

            try:
                lines = path.read_text(
                    encoding="utf-8"
                ).splitlines()
            except (
                UnicodeDecodeError,
                OSError,
            ):
                continue

            for number, line in enumerate(
                lines,
                start=1,
            ):
                candidate = (
                    line
                    if case_sensitive
                    else line.lower()
                )

                if needle in candidate:
                    results.append(
                        SearchResult(
                            file=str(
                                path.relative_to(
                                    self.root
                                )
                            ),
                            line=number,
                            text=line,
                            score=1.0,
                        )
                    )

        return results

    def symbols(
        self,
        query: str,
    ) -> List[SearchResult]:
        if self.index is None:
            return []

        query = query.lower()

        results: list[SearchResult] = []

        for symbol in self.index.symbols.all():
            if (
                query in symbol.name.lower()
                or query in symbol.qualified_name.lower()
            ):
                results.append(
                    SearchResult(
                        file=symbol.file or "",
                        line=symbol.line,
                        text=symbol.qualified_name,
                        score=1.0,
                    )
                )

        return results