from __future__ import annotations

from pathlib import Path

from ..ir import DiagramIR
from ..renderers.svg import SVGRenderer


def export_svg(
    diagram: DiagramIR,
    output_path: str | Path,
    *,
    theme: str = "light",
) -> Path:

    output = Path(output_path)

    svg = SVGRenderer().render(
        diagram,
        theme=theme,
    )

    output.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    output.write_text(
        svg,
        encoding="utf-8",
    )

    return output