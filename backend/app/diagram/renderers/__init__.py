from abc import ABC, abstractmethod
from typing import Tuple
from app.diagram.models import (
    DiagramFormat,
    DiagramIR,
    DiagramOutputSpec,
    DiagramSize,
)
from app.diagram.design.tokens import DiagramTheme


class DiagramRenderer(ABC):
    """Abstract base interface for all deterministic diagram renderers."""

    DIMENSION_MAP: dict[DiagramSize, Tuple[int, int]] = {
        DiagramSize.DOC_INLINE: (640, 360),
        DiagramSize.DOC_WIDE: (960, 540),
        DiagramSize.SLIDE_16X9: (1280, 720),
        DiagramSize.SLIDE_4X3: (1024, 768),
        DiagramSize.SOCIAL_OG: (1200, 630),
        DiagramSize.SOCIAL_SQUARE: (1080, 1080),
        DiagramSize.PRINT_A4: (1240, 1754),
        DiagramSize.PRINT_LETTER: (1275, 1650),
        DiagramSize.FIT: (800, 600),
    }

    def resolve_dimensions(self, output_spec: DiagramOutputSpec) -> Tuple[int, int]:
        return self.DIMENSION_MAP.get(output_spec.size, (960, 540))

    @abstractmethod
    def render(
        self,
        diagram: DiagramIR,
        theme: DiagramTheme,
        output_spec: DiagramOutputSpec,
    ) -> str:
        """Deterministically render the diagram to a target format string."""
        raise NotImplementedError


# Import concrete implementations
from app.diagram.renderers.svg import SVGRenderer
from app.diagram.renderers.html import HTMLRenderer
from app.diagram.renderers.png import PNGRenderer


def get_renderer(format_type: DiagramFormat) -> DiagramRenderer:
    """Factory helper to instantiate the appropriate renderer for a given format."""
    registry: dict[DiagramFormat, type[DiagramRenderer]] = {
        DiagramFormat.SVG: SVGRenderer,
        DiagramFormat.HTML: HTMLRenderer,
        DiagramFormat.PNG: PNGRenderer,
    }

    renderer_cls = registry.get(format_type)
    if not renderer_cls:
        raise ValueError(f"Unsupported diagram format: {format_type}")

    return renderer_cls()


__all__ = [
    "DiagramRenderer",
    "SVGRenderer",
    "HTMLRenderer",
    "PNGRenderer",
    "get_renderer",
]