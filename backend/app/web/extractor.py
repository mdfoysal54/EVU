from __future__ import annotations

import html
import re
from html.parser import HTMLParser


class HTMLTextExtractor(HTMLParser):
    """
    Small standard-library HTML-to-text extractor.

    It does not execute JavaScript.
    """

    BLOCK_TAGS = {
        "address",
        "article",
        "aside",
        "blockquote",
        "br",
        "div",
        "dl",
        "dt",
        "dd",
        "fieldset",
        "figcaption",
        "figure",
        "footer",
        "form",
        "h1",
        "h2",
        "h3",
        "h4",
        "h5",
        "h6",
        "header",
        "hr",
        "li",
        "main",
        "nav",
        "ol",
        "p",
        "pre",
        "section",
        "table",
        "td",
        "th",
        "tr",
        "ul",
    }

    IGNORED_TAGS = {
        "script",
        "style",
        "noscript",
        "template",
        "svg",
        "canvas",
    }

    def __init__(self):
        super().__init__(
            convert_charrefs=True
        )

        self.parts: list[str] = []
        self.ignore_depth = 0

    def handle_starttag(
        self,
        tag: str,
        attrs,
    ):
        tag = tag.lower()

        if tag in self.IGNORED_TAGS:
            self.ignore_depth += 1
            return

        if self.ignore_depth > 0:
            return

        if tag in self.BLOCK_TAGS:
            self.parts.append("\n")

    def handle_endtag(self, tag: str):
        tag = tag.lower()

        if tag in self.IGNORED_TAGS:
            if self.ignore_depth > 0:
                self.ignore_depth -= 1

            return

        if self.ignore_depth > 0:
            return

        if tag in self.BLOCK_TAGS:
            self.parts.append("\n")

    def handle_data(self, data: str):
        if self.ignore_depth > 0:
            return

        if not data:
            return

        self.parts.append(data)

    def get_text(self) -> str:
        return "".join(self.parts)


class WebTextExtractor:
    """
    Converts HTML or plain text into bounded readable text.
    """

    def __init__(
        self,
        max_chars: int = 30_000,
    ):
        self.max_chars = max_chars

    @staticmethod
    def clean_text(text: str) -> str:
        if not text:
            return ""

        text = html.unescape(text)

        # Normalize different whitespace characters.
        text = text.replace("\r\n", "\n")
        text = text.replace("\r", "\n")
        text = text.replace("\t", " ")

        # Remove excessive spaces.
        text = re.sub(
            r"[ \u00a0]+",
            " ",
            text,
        )

        # Remove spaces around line breaks.
        text = re.sub(
            r" *\n *",
            "\n",
            text,
        )

        # Collapse 3+ blank lines.
        text = re.sub(
            r"\n{3,}",
            "\n\n",
            text,
        )

        # Remove empty lines containing only spaces.
        lines = [
            line.strip()
            for line in text.splitlines()
        ]

        cleaned_lines: list[str] = []

        previous_blank = False

        for line in lines:
            if not line:
                if not previous_blank:
                    cleaned_lines.append("")

                previous_blank = True
                continue

            cleaned_lines.append(line)
            previous_blank = False

        return "\n".join(
            cleaned_lines
        ).strip()

    def extract_html(
        self,
        html_content: str,
    ) -> str:

        if not html_content:
            return ""

        parser = HTMLTextExtractor()

        try:
            parser.feed(html_content)
            parser.close()
        except Exception:
            # If malformed HTML causes a parser error,
            # fall back to raw content cleaning.
            return self.clean_text(
                html_content[: self.max_chars]
            )

        text = parser.get_text()

        text = self.clean_text(text)

        return text[: self.max_chars]

    def extract(
        self,
        content: str,
        content_type: str = "",
    ) -> str:

        content_type = (
            content_type or ""
        ).lower()

        if (
            "html" in content_type
            or "xhtml" in content_type
        ):
            return self.extract_html(content)

        # Plain text / JSON / unknown content.
        return self.clean_text(
            content[: self.max_chars]
        )


web_text_extractor = WebTextExtractor()