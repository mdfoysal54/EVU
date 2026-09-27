import html
from app.diagram.models import DiagramIR
from app.diagram.design.tokens import DiagramTheme, DEFAULT_THEME

class SVGRenderer:
    def __init__(self, theme: DiagramTheme = DEFAULT_THEME):
        self.theme = theme

    def render(self, diagram: DiagramIR, width: int = 800, height: int = 600) -> str:
        css = self.theme.to_css_variables()
        escaped_title = html.escape(diagram.title)

        svg_parts = [
            f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" '
            f'width="{width}" height="{height}" role="img" aria-labelledby="title desc">',
            f'  <title id="title">{escaped_title}</title>',
            f'  <desc id="desc">Diagram showing {escaped_title} with {len(diagram.nodes)} components</desc>',
            f'  <style>',
            css,
            '    .canvas { fill: var(--paper); }',
            '    .node-box { fill: var(--paper-2); stroke: var(--accent); stroke-width: 2px; rx: 6px; }',
            '    .node-text { fill: var(--ink); font-family: var(--body-font); font-size: 14px; text-anchor: middle; dominant-baseline: middle; }',
            '    .edge-line { stroke: var(--muted); stroke-width: 2px; marker-end: url(#arrow); }',
            '  </style>',
            '  <defs>',
            '    <marker id="arrow" viewBox="0 0 10 10" refX="5" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">',
            '      <path d="M 0 0 L 10 5 L 0 10 z" fill="var(--muted)" />',
            '    </marker>',
            '  </defs>',
            f'  <rect width="100%" height="100%" class="canvas" />',
            '  <g class="diagram-content">'
        ]

        # Simple linear layout fallback for deterministic node positioning
        node_positions = {}
        spacing = width // (len(diagram.nodes) + 1 or 1)
        for idx, node in enumerate(diagram.nodes):
            cx, cy = (idx + 1) * spacing, height // 2
            node_positions[node.id] = (cx, cy)
            svg_parts.append(
                f'    <rect x="{cx - 60}" y="{cy - 25}" width="120" height="50" class="node-box" />'
            )
            svg_parts.append(
                f'    <text x="{cx}" y="{cy}" class="node-text">{html.escape(node.label)}</text>'
            )

        for edge in diagram.edges:
            if edge.source in node_positions and edge.target in node_positions:
                x1, y1 = node_positions[edge.source]
                x2, y2 = node_positions[edge.target]
                svg_parts.append(
                    f'    <line x1="{x1 + 60}" y1="{y1}" x2="{x2 - 60}" y2="{y2}" class="edge-line" />'
                )

        svg_parts.append('  </g>')
        svg_parts.append('</svg>')
        return "\n".join(svg_parts)