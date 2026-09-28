from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List

from .scanner import CodebaseScanner
from .parser import PythonParser, ParsedFile
from .symbols import Symbol, SymbolTable
from .graph import CodeGraph, GraphNode, GraphEdge


@dataclass
class CodebaseIndex:
    files: Dict[str, ParsedFile] = field(
        default_factory=dict
    )

    symbols: SymbolTable = field(
        default_factory=SymbolTable
    )

    graph: CodeGraph = field(
        default_factory=CodeGraph
    )


class CodebaseIndexer:
    def __init__(
        self,
        root: Path | str,
    ) -> None:
        self.root = Path(root).resolve()

        self.scanner = CodebaseScanner(
            self.root
        )

        self.parser = PythonParser(
            self.root
        )

        self.index = CodebaseIndex()

    def build(self) -> CodebaseIndex:
        source_files = self.scanner.scan()

        for source_file in source_files:
            if source_file.extension != ".py":
                continue

            parsed = self.parser.parse_file(
                source_file.path
            )

            key = source_file.relative_path

            self.index.files[key] = parsed

            for symbol in parsed.symbols:
                symbol.file = key

                self.index.symbols.add(symbol)

                node_id = (
                    f"symbol:{key}:"
                    f"{symbol.qualified_name}"
                )

                self.index.graph.add_node(
                    GraphNode(
                        node_id=node_id,
                        node_type="symbol",
                        name=symbol.qualified_name,
                        metadata={
                            "file": key,
                            "line": symbol.line,
                            "kind": symbol.kind.value,
                        },
                    )
                )

            module_node_id = (
                f"module:{key}"
            )

            self.index.graph.add_node(
                GraphNode(
                    node_id=module_node_id,
                    node_type="module",
                    name=parsed.module,
                    metadata={
                        "file": key,
                    },
                )
            )

            for imported in parsed.imports:
                imported_node = (
                    f"import:{imported}"
                )

                if imported_node not in self.index.graph.nodes:
                    self.index.graph.add_node(
                        GraphNode(
                            node_id=imported_node,
                            node_type="import",
                            name=imported,
                        )
                    )

                self.index.graph.add_edge(
                    GraphEdge(
                        source=module_node_id,
                        target=imported_node,
                        relation="imports",
                    )
                )

        return self.index

    def get_file(
        self,
        relative_path: str,
    ) -> ParsedFile | None:
        return self.index.files.get(
            relative_path
        )