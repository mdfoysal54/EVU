from __future__ import annotations

from pathlib import Path

from ..ir import DiagramIR
from ..renderers.png import PNGRenderer


def export_png(
    diagram: DiagramIR,
    output_path: str | Path,
    *,
    theme: str = "light",
) -> Path:

    output = Path(output_path)

    output.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    PNGRenderer().render(
        diagram,
        output_path=output,
        theme=theme,
    )

    return output