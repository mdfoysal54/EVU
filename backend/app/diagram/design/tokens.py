from dataclasses import dataclass

@dataclass
class DiagramTheme:
    paper: str
    paper_2: str
    ink: str
    muted: str
    accent: str
    link: str
    title_font: str = "Inter, sans-serif"
    body_font: str = "Inter, sans-serif"
    mono_font: str = "ui-monospace, monospace"

    def to_css_variables(self) -> str:
        return f"""
        :root {{
            --paper: {self.paper};
            --paper-2: {self.paper_2};
            --ink: {self.ink};
            --muted: {self.muted};
            --accent: {self.accent};
            --link: {self.link};
            --title-font: {self.title_font};
            --body-font: {self.body_font};
            --mono-font: {self.mono_font};
        }}
        """

DEFAULT_THEME = DiagramTheme(
    paper="#f8f6f0",
    paper_2="#ffffff",
    ink="#111111",
    muted="#6b6b68",
    accent="#c73a2b",
    link="#2463a8",
)