from __future__ import annotations

from dataclasses import dataclass

from .tokens import (
    ColorTokens,
    DesignTokens,
)


@dataclass(frozen=True)
class DiagramTheme:
    name: str
    tokens: DesignTokens
    font_family: str = (
        "Inter, Arial, Helvetica, sans-serif"
    )


LIGHT_THEME = DiagramTheme(
    name="light",
    tokens=DesignTokens(),
)


DARK_THEME = DiagramTheme(
    name="dark",
    tokens=DesignTokens(
        colors=ColorTokens(
            background="#0F172A",
            surface="#1E293B",
            text="#F8FAFC",
            muted_text="#94A3B8",
            border="#475569",
            primary="#60A5FA",
            secondary="#A78BFA",
            success="#4ADE80",
            warning="#FBBF24",
            danger="#F87171",
        )
    ),
)


THEMES = {
    "light": LIGHT_THEME,
    "dark": DARK_THEME,
}


def get_theme(name: str = "light") -> DiagramTheme:
    normalized = name.lower().strip()

    if normalized not in THEMES:
        raise ValueError(
            f"Unknown diagram theme: {name}"
        )

    return THEMES[normalized]