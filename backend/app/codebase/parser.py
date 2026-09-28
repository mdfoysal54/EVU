from __future__ import annotations

import ast
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional

from .symbols import Symbol, SymbolKind


@dataclass
class ParsedFile:
    path: Path
    module: str
    tree: ast.AST
    symbols: List[Symbol] = field(
        default_factory=list
    )
    imports: List[str] = field(
        default_factory=list
    )
    errors: List[str] = field(
        default_factory=list
    )


class PythonParser:
    def __init__(
        self,
        root: Optional[Path | str] = None,
    ) -> None:
        self.root = (
            Path(root).resolve()
            if root is not None
            else None
        )

    def parse_file(
        self,
        path: Path | str,
    ) -> ParsedFile:
        path = Path(path)

        source = path.read_text(
            encoding="utf-8"
        )

        try:
            tree = ast.parse(
                source,
                filename=str(path),
            )
        except SyntaxError as exc:
            return ParsedFile(
                path=path,
                module=self.module_name(path),
                tree=ast.Module(body=[]),
                errors=[str(exc)],
            )

        parsed = ParsedFile(
            path=path,
            module=self.module_name(path),
            tree=tree,
        )

        parsed.imports = self._imports(tree)
        parsed.symbols = self._symbols(tree)

        return parsed

    def module_name(
        self,
        path: Path,
    ) -> str:
        if self.root is not None:
            try:
                relative = path.resolve().relative_to(
                    self.root
                )
            except ValueError:
                relative = path
        else:
            relative = path

        parts = list(relative.with_suffix("").parts)

        if parts and parts[-1] == "__init__":
            parts = parts[:-1]

        return ".".join(parts)

    @staticmethod
    def _imports(
        tree: ast.AST,
    ) -> List[str]:
        imports: list[str] = []

        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.append(alias.name)

            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    imports.append(node.module)

        return sorted(set(imports))

    def _symbols(
        self,
        tree: ast.AST,
    ) -> List[Symbol]:
        symbols: list[Symbol] = []

        for node in tree.body:
            symbols.extend(
                self._extract_node(
                    node,
                    parent=None,
                )
            )

        return symbols

    def _extract_node(
        self,
        node: ast.AST,
        parent: Optional[str],
    ) -> List[Symbol]:
        results: list[Symbol] = []

        if isinstance(node, ast.ClassDef):
            symbol = Symbol(
                name=node.name,
                qualified_name=(
                    f"{parent}.{node.name}"
                    if parent
                    else node.name
                ),
                kind=SymbolKind.CLASS,
                line=getattr(node, "lineno", 0),
                end_line=getattr(
                    node,
                    "end_lineno",
                    getattr(node, "lineno", 0),
                ),
                parent=parent,
            )

            results.append(symbol)

            for child in node.body:
                results.extend(
                    self._extract_node(
                        child,
                        symbol.qualified_name,
                    )
                )

        elif isinstance(
            node,
            (ast.FunctionDef, ast.AsyncFunctionDef),
        ):
            symbol = Symbol(
                name=node.name,
                qualified_name=(
                    f"{parent}.{node.name}"
                    if parent
                    else node.name
                ),
                kind=SymbolKind.FUNCTION,
                line=getattr(node, "lineno", 0),
                end_line=getattr(
                    node,
                    "end_lineno",
                    getattr(node, "lineno", 0),
                ),
                parent=parent,
            )

            results.append(symbol)

        elif isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name):
                    results.append(
                        Symbol(
                            name=target.id,
                            qualified_name=(
                                f"{parent}.{target.id}"
                                if parent
                                else target.id
                            ),
                            kind=SymbolKind.VARIABLE,
                            line=getattr(
                                node,
                                "lineno",
                                0,
                            ),
                            end_line=getattr(
                                node,
                                "end_lineno",
                                getattr(
                                    node,
                                    "lineno",
                                    0,
                                ),
                            ),
                            parent=parent,
                        )
                    )

        return results