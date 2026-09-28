from __future__ import annotations

from pathlib import Path

from ..ir import DiagramIR
from ..renderers.svg import SVGRenderer


def export_pdf(
    diagram: DiagramIR,
    output_path: str | Path,
    *,
    theme: str = "light",
) -> Path:

    output = Path(output_path)

    try:
        import cairosvg
    except ImportError as exc:
        raise RuntimeError(
            "PDF export requires CairoSVG. "
            "Install it with: pip install cairosvg"
        ) from exc

    svg = SVGRenderer().render(
        diagram,
        theme=theme,
    )

    output.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    cairosvg.svg2pdf(
        bytestring=svg.encode("utf-8"),
        write_to=str(output),
    )

    return output