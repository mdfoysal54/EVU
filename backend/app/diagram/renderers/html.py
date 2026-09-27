from app.diagram.models import DiagramIR, DiagramOutputSpec
from app.diagram.design.tokens import DiagramTheme
from app.diagram.renderers import DiagramRenderer
from app.diagram.renderers.svg import SVGRenderer


class HTMLRenderer(DiagramRenderer):

    def __init__(self):
        self.svg_renderer = SVGRenderer()

    def render(
        self,
        diagram: DiagramIR,
        theme: DiagramTheme,
        output_spec: DiagramOutputSpec,
    ) -> str:
        svg_content = self.svg_renderer.render(diagram, theme, output_spec)

        return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>{diagram.title}</title>
  <style>
    body {{
      margin: 0;
      padding: 24px;
      display: flex;
      justify-content: center;
      align-items: center;
      background: {theme.paper};
      font-family: {theme.body_font};
    }}
    .diagram-wrapper {{
      max-width: 100%;
      box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
      border-radius: 8px;
      overflow: hidden;
    }}
  </style>
</head>
<body>
  <div class="diagram-wrapper">
    {svg_content}
  </div>
</body>
</html>
"""