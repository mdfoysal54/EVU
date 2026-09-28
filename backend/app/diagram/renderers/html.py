from __future__ import annotations

from html import escape

from ..ir import DiagramIR
from .svg import SVGRenderer


class HTMLRenderer:
    name = "html"

    def render(
        self,
        diagram: DiagramIR,
        *,
        svg: str | None = None,
        title: str | None = None,
    ) -> str:

        svg_content = svg or SVGRenderer().render(
            diagram
        )

        safe_title = escape(
            title or diagram.title or "EVU Diagram"
        )

        return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport"
      content="width=device-width, initial-scale=1.0">
<title>{safe_title}</title>
<style>
html, body {{
    margin: 0;
    padding: 0;
    min-height: 100%;
    font-family:
        Inter, Arial, Helvetica, sans-serif;
    background: #f8fafc;
}}

.diagram-container {{
    padding: 32px;
    overflow: auto;
}}

.diagram-container svg {{
    display: block;
    max-width: 100%;
    height: auto;
}}
</style>
</head>
<body>
<div class="diagram-container">
{svg_content}
</div>
</body>
</html>
"""