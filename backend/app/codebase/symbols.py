from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional


class SymbolKind(str, Enum):
    MODULE = "module"
    CLASS = "class"
    FUNCTION = "function"
    VARIABLE = "variable"
    METHOD = "method"
    IMPORT = "import"


@dataclass
class Symbol:
    name: str
    qualified_name: str
    kind: SymbolKind

    line: int = 0
    end_line: int = 0

    file: Optional[str] = None
    parent: Optional[str] = None

    metadata: Dict[str, object] = field(
        default_factory=dict
    )


class SymbolTable:
    def __init__(self) -> None:
        self._symbols: Dict[
            str,
            List[Symbol],
        ] = {}

    def add(
        self,
        symbol: Symbol,
    ) -> None:
        self._symbols.setdefault(
            symbol.name,
            [],
        ).append(symbol)

    def add_many(
        self,
        symbols: List[Symbol],
    ) -> None:
        for symbol in symbols:
            self.add(symbol)

    def lookup(
        self,
        name: str,
    ) -> List[Symbol]:
        return list(
            self._symbols.get(
                name,
                [],
            )
        )

    def all(self) -> List[Symbol]:
        results: list[Symbol] = []

        for symbols in self._symbols.values():
            results.extend(symbols)

        return results

    def qualified(
        self,
        qualified_name: str,
    ) -> Optional[Symbol]:
        for symbol in self.all():
            if symbol.qualified_name == qualified_name:
                return symbol

        return None