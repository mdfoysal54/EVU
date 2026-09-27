from dataclasses import dataclass
from typing import Optional
from app.diagram.design.tokens import DiagramTheme, DEFAULT_THEME
from app.diagram.design.contrast import passes_wcag_aa

@dataclass
class BrandProfile:
    name: str
    paper: str
    paper_2: str
    ink: str
    muted: str
    accent: str
    link: str
    title_font: str = "Inter, sans-serif"
    body_font: str = "Inter, sans-serif"
    mono_font: str = "ui-monospace, monospace"
    source: Optional[str] = None
    confidence: float = 0.0

    def to_diagram_theme(self) -> DiagramTheme:
        # Fallback to defaults if extracted colors fail WCAG AA contrast check
        validated_ink = self.ink if passes_wcag_aa(self.ink, self.paper) else DEFAULT_THEME.ink
        validated_muted = self.muted if passes_wcag_aa(self.muted, self.paper) else DEFAULT_THEME.muted
        
        return DiagramTheme(
            paper=self.paper,
            paper_2=self.paper_2,
            ink=validated_ink,
            muted=validated_muted,
            accent=self.accent,
            link=self.link,
            title_font=self.title_font,
            body_font=self.body_font,
            mono_font=self.mono_font,
        )