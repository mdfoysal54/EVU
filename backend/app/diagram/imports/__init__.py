from .drawio import (
    DrawioImporter,
    parse_drawio,
)
from .excalidraw import (
    ExcalidrawImporter,
    parse_excalidraw,
)
from .mermaid import (
    MermaidImporter,
    parse_mermaid,
)


IMPORTERS = {
    "mermaid": MermaidImporter,
    "drawio": DrawioImporter,
    "excalidraw": ExcalidrawImporter,
}


def get_importer(name: str):
    importer = IMPORTERS.get(
        name.lower().strip()
    )

    if importer is None:
        raise ValueError(
            f"Unknown diagram importer: {name}"
        )

    return importer()


__all__ = [
    "MermaidImporter",
    "DrawioImporter",
    "ExcalidrawImporter",
    "parse_mermaid",
    "parse_drawio",
    "parse_excalidraw",
    "IMPORTERS",
    "get_importer",
]