from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class ColorTokens:
    background: str = "#FFFFFF"
    surface: str = "#F8FAFC"
    text: str = "#0F172A"
    muted_text: str = "#64748B"
    border: str = "#CBD5E1"
    primary: str = "#2563EB"
    secondary: str = "#7C3AED"
    success: str = "#16A34A"
    warning: str = "#D97706"
    danger: str = "#DC2626"


@dataclass(frozen=True)
class SpacingTokens:
    xs: int = 4
    sm: int = 8
    md: int = 16
    lg: int = 24
    xl: int = 32
    xxl: int = 48


@dataclass(frozen=True)
class RadiusTokens:
    sm: int = 4
    md: int = 8
    lg: int = 12
    pill: int = 999


@dataclass(frozen=True)
class DesignTokens:
    colors: ColorTokens = field(
        default_factory=ColorTokens
    )
    spacing: SpacingTokens = field(
        default_factory=SpacingTokens
    )
    radius: RadiusTokens = field(
        default_factory=RadiusTokens
    )