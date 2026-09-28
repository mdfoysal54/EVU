from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class TypographyStyle:
    font_family: str = (
        "Inter, Arial, Helvetica, sans-serif"
    )
    title_size: int = 28
    heading_size: int = 20
    body_size: int = 14
    small_size: int = 12
    font_weight_normal: int = 400
    font_weight_medium: int = 500
    font_weight_bold: int = 700


DEFAULT_TYPOGRAPHY = TypographyStyle()


def css_font_family(style: TypographyStyle | None = None) -> str:
    style = style or DEFAULT_TYPOGRAPHY

    return (
        "font-family: "
        + style.font_family
        + ";"
    )