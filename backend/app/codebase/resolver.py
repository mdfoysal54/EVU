from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional

from .indexer import CodebaseIndex
from .symbols import Symbol


@dataclass
class ResolvedSymbol:
    symbol: Symbol
    confidence: float
    reason: str


class SymbolResolver:
    def __init__(
        self,
        index: CodebaseIndex,
    ) -> None:
        self.index = index

    def resolve(
        self,
        name: str,
        file: Optional[str] = None,
    ) -> List[ResolvedSymbol]:
        candidates = self.index.symbols.lookup(
            name
        )

        results: list[ResolvedSymbol] = []

        for symbol in candidates:
            if (
                file is not None
                and symbol.file != file
            ):
                continue

            confidence = 0.5
            reason = "name match"

            if symbol.qualified_name == name:
                confidence = 1.0
                reason = "qualified name match"

            elif symbol.file == file:
                confidence = 0.9
                reason = "same-file name match"

            results.append(
                ResolvedSymbol(
                    symbol=symbol,
                    confidence=confidence,
                    reason=reason,
                )
            )

        return sorted(
            results,
            key=lambda item: item.confidence,
            reverse=True,
        )

    def resolve_qualified(
        self,
        qualified_name: str,
    ) -> Optional[ResolvedSymbol]:
        symbol = self.index.symbols.qualified(
            qualified_name
        )

        if symbol is None:
            return None

        return ResolvedSymbol(
            symbol=symbol,
            confidence=1.0,
            reason="qualified lookup",
        )