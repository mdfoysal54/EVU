from __future__ import annotations

import html
import re


SCRIPT_PATTERN = re.compile(
    r"<\s*script\b[^>]*>.*?"
    r"<\s*/\s*script\s*>",
    re.IGNORECASE | re.DOTALL,
)

EVENT_HANDLER_PATTERN = re.compile(
    r"\s+on[a-zA-Z]+\s*=\s*"
    r"(?:\"[^\"]*\"|'[^']*'|[^\s>]+)",
    re.IGNORECASE,
)

JAVASCRIPT_URL_PATTERN = re.compile(
    r"javascript\s*:",
    re.IGNORECASE,
)

DANGEROUS_TAG_PATTERN = re.compile(
    r"<\s*(iframe|object|embed|applet|form)\b[^>]*>",
    re.IGNORECASE,
)


class DiagramSanitizer:
    """
    Sanitizes untrusted diagram-related text.

    This is intentionally conservative.
    """

    def sanitize_text(
        self,
        value: str,
        *,
        max_length: int = 10000,
    ) -> str:

        if not isinstance(value, str):
            value = str(value)

        value = value[:max_length]

        value = SCRIPT_PATTERN.sub(
            "",
            value,
        )

        value = EVENT_HANDLER_PATTERN.sub(
            "",
            value,
        )

        value = JAVASCRIPT_URL_PATTERN.sub(
            "",
            value,
        )

        value = DANGEROUS_TAG_PATTERN.sub(
            "",
            value,
        )

        return value.strip()

    def escape_text(
        self,
        value: str,
    ) -> str:

        return html.escape(
            self.sanitize_text(value)
        )

    def sanitize_svg(
        self,
        svg: str,
    ) -> str:

        svg = self.sanitize_text(
            svg,
            max_length=2_000_000,
        )

        svg = re.sub(
            r"<script\b[^>]*>.*?</script>",
            "",
            svg,
            flags=re.IGNORECASE | re.DOTALL,
        )

        svg = re.sub(
            r"on[a-zA-Z]+\s*=",
            "data-blocked-event=",
            svg,
            flags=re.IGNORECASE,
        )

        svg = re.sub(
            r"javascript\s*:",
            "",
            svg,
            flags=re.IGNORECASE,
        )

        return svg


def sanitize_text(value: str) -> str:
    return DiagramSanitizer().sanitize_text(value)


def sanitize_svg(svg: str) -> str:
    return DiagramSanitizer().sanitize_svg(svg)