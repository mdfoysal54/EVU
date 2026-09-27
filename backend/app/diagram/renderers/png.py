import base64
from app.diagram.models import DiagramIR, DiagramOutputSpec
from app.diagram.design.tokens import DiagramTheme
from app.diagram.renderers import DiagramRenderer
from app.diagram.renderers.svg import SVGRenderer


class PNGRenderer(DiagramRenderer):

    def __init__(self):
        self.svg_renderer = SVGRenderer()

    def render(
        self,
        diagram: DiagramIR,
        theme: DiagramTheme,
        output_spec: DiagramOutputSpec,
    ) -> str:
        """
        Renders the SVG and converts it to a base64-encoded PNG string.
        Requires cairosvg (`pip install cairosvg`).
        """
        svg_str = self.svg_renderer.render(diagram, theme, output_spec)
        try:
            import cairosvg  # type: ignore[import-untyped, import-not-found]

            png_bytes = cairosvg.svg2png(bytestring=svg_str.encode("utf-8"))
            return base64.b64encode(png_bytes).decode("utf-8")
        except ImportError:
            raise RuntimeError(
                "cairosvg is required for raster PNG rendering. Install with: pip install cairosvg"
            )