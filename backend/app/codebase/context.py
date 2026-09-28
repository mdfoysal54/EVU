from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional

from .indexer import CodebaseIndex
from .resolver import SymbolResolver
from .search import CodeSearch


@dataclass
class CodeContext:
    query: str

    files: List[str] = field(
        default_factory=list
    )

    symbols: List[str] = field(
        default_factory=list
    )

    snippets: List[str] = field(
        default_factory=list
    )

    metadata: dict = field(
        default_factory=dict
    )

    def as_text(self) -> str:
        sections: list[str] = []

        if self.files:
            sections.append(
                "FILES:\n"
                + "\n".join(self.files)
            )

        if self.symbols:
            sections.append(
                "SYMBOLS:\n"
                + "\n".join(self.symbols)
            )

        if self.snippets:
            sections.append(
                "CODE:\n"
                + "\n\n".join(self.snippets)
            )

        return "\n\n".join(sections)


class CodeContextBuilder:
    def __init__(
        self,
        root: Path | str,
        index: CodebaseIndex,
    ) -> None:
        self.root = Path(root).resolve()
        self.index = index

        self.search = CodeSearch(
            self.root,
            index,
        )

        self.resolver = SymbolResolver(
            index
        )

    def build(
        self,
        query: str,
        max_files: int = 10,
        max_snippets: int = 10,
    ) -> CodeContext:
        context = CodeContext(
            query=query
        )

        text_results = self.search.text(
            query
        )

        symbol_results = self.search.symbols(
            query
        )

        context.files = [
            result.file
            for result in text_results[:max_files]
        ]

        context.symbols = [
            result.text
            for result in symbol_results[:max_files]
        ]

        for result in text_results[
            :max_snippets
        ]:
            path = (
                self.root
                / result.file
            )

            try:
                lines = path.read_text(
                    encoding="utf-8"
                ).splitlines()

                start = max(
                    0,
                    result.line - 3,
                )

                end = min(
                    len(lines),
                    result.line + 2,
                )

                snippet = (
                    f"# {result.file}:"
                    f"{result.line}\n"
                    + "\n".join(
                        lines[start:end]
                    )
                )

                context.snippets.append(
                    snippet
                )

            except (
                OSError,
                UnicodeDecodeError,
            ):
                continue

        context.metadata = {
            "query": query,
            "file_count": len(context.files),
            "symbol_count": len(context.symbols),
            "snippet_count": len(
                context.snippets
            ),
        }

        return context