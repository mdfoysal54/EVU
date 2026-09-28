from __future__ import annotations

from pathlib import Path

from ..ir import DiagramIR
from .svg import SVGRenderer


class PNGRenderer:
    name = "png"

    def render(
        self,
        diagram: DiagramIR,
        *,
        output_path: str | Path | None = None,
        theme: str = "light",
    ) -> bytes:

        svg = SVGRenderer().render(
            diagram,
            theme=theme,
        )

        try:
            import cairosvg  # type: ignore[import-not-found]
        except ImportError as exc:
            raise RuntimeError(
                "PNG rendering requires CairoSVG. "
                "Install it with: pip install cairosvg"
            ) from exc

        png_bytes = cairosvg.svg2png(
            bytestring=svg.encode("utf-8")
        )

        if output_path is not None:
            Path(output_path).write_bytes(
                png_bytes
            )

        return png_bytes