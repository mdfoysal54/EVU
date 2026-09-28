from __future__ import annotations

from html import escape

from ..design import get_theme
from ..ir import DiagramIR
from ..layout import LayoutResult, get_layout


class SVGRenderer:
    name = "svg"

    def render(
        self,
        diagram: DiagramIR,
        *,
        layout: LayoutResult | None = None,
        theme: str = "light",
    ) -> str:

        if layout is None:
            layout = get_layout(
                "graph"
            ).layout(diagram)

        diagram_theme = get_theme(theme)
        colors = diagram_theme.tokens.colors

        parts = [
            (
                '<svg xmlns="http://www.w3.org/2000/svg" '
                f'width="{layout.width}" '
                f'height="{layout.height}" '
                f'viewBox="0 0 {layout.width} {layout.height}">'
            ),
            (
                "<rect "
                f'width="{layout.width}" '
                f'height="{layout.height}" '
                f'fill="{colors.background}"/>'
            ),
        ]

        # Edges first so nodes appear above them.
        for edge in diagram.edges:
            source = layout.get(edge.source)
            target = layout.get(edge.target)

            if not source or not target:
                continue

            x1 = source.x + source.width / 2
            y1 = source.y + source.height / 2

            x2 = target.x + target.width / 2
            y2 = target.y + target.height / 2

            dash = ""

            if edge.style.value == "dashed":
                dash = ' stroke-dasharray="8 6"'
            elif edge.style.value == "dotted":
                dash = ' stroke-dasharray="2 5"'

            parts.append(
                f'<line x1="{x1}" y1="{y1}" '
                f'x2="{x2}" y2="{y2}" '
                f'stroke="{colors.border}" '
                f'stroke-width="2"{dash}/>'
            )

            if edge.label:
                mid_x = (x1 + x2) / 2
                mid_y = (y1 + y2) / 2

                parts.append(
                    f'<text x="{mid_x}" y="{mid_y - 5}" '
                    f'text-anchor="middle" '
                    f'font-family="{escape(diagram_theme.font_family)}" '
                    f'font-size="11" '
                    f'fill="{colors.muted_text}">'
                    f'{escape(edge.label)}'
                    "</text>"
                )

        for node in diagram.nodes:
            position = layout.get(node.id)

            if not position:
                continue

            x = position.x
            y = position.y
            width = position.width
            height = position.height

            fill = colors.surface
            stroke = colors.primary

            parts.append(
                f'<rect x="{x}" y="{y}" '
                f'width="{width}" height="{height}" '
                f'rx="10" '
                f'fill="{fill}" '
                f'stroke="{stroke}" '
                f'stroke-width="2"/>'
            )

            text_x = x + width / 2
            text_y = y + height / 2 + 5

            parts.append(
                f'<text x="{text_x}" y="{text_y}" '
                f'text-anchor="middle" '
                f'font-family="{escape(diagram_theme.font_family)}" '
                f'font-size="14" '
                f'fill="{colors.text}">'
                f'{escape(node.label)}'
                "</text>"
            )

        if diagram.title:
            parts.append(
                f'<text x="{layout.width / 2}" y="28" '
                f'text-anchor="middle" '
                f'font-family="{escape(diagram_theme.font_family)}" '
                f'font-size="18" '
                f'font-weight="700" '
                f'fill="{colors.text}">'
                f'{escape(diagram.title)}'
                "</text>"
            )

        parts.append("</svg>")

        return "\n".join(parts)