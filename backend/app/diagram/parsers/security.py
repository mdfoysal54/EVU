from __future__ import annotations

import html
import re
from dataclasses import dataclass, field
from typing import Iterable


@dataclass
class ParserSecurityConfig:
    """
    Security configuration for imported diagram documents.
    """

    max_input_size: int = 5 * 1024 * 1024

    max_lines: int = 100_000

    max_line_length: int = 100_000

    allow_scripts: bool = False

    allow_external_urls: bool = False

    allow_data_urls: bool = False

    allowed_schemes: set[str] = field(
        default_factory=lambda: {
            "http",
            "https",
        }
    )


@dataclass
class SecurityFinding:
    """
    Security issue detected in parser input.
    """

    code: str
    message: str
    severity: str = "error"
    line: int | None = None


class ParserSecurityError(ValueError):
    """
    Raised when parser input violates security policy.
    """

    def __init__(
        self,
        message: str,
        findings: Iterable[
            SecurityFinding
        ] | None = None,
    ) -> None:
        super().__init__(message)

        self.findings = list(
            findings or []
        )


class DiagramParserSecurity:
    """
    Defensive validation/sanitization layer for imported diagrams.

    It is intentionally format-agnostic.
    """

    SCRIPT_PATTERN = re.compile(
        r"<\s*script\b",
        re.IGNORECASE,
    )

    EVENT_HANDLER_PATTERN = re.compile(
        r"\bon[a-z]+\s*=",
        re.IGNORECASE,
    )

    JAVASCRIPT_URL_PATTERN = re.compile(
        r"(?:javascript|vbscript)\s*:",
        re.IGNORECASE,
    )

    DATA_URL_PATTERN = re.compile(
        r"\bdata\s*:",
        re.IGNORECASE,
    )

    EXTERNAL_URL_PATTERN = re.compile(
        r"https?://",
        re.IGNORECASE,
    )

    XML_ENTITY_PATTERN = re.compile(
        r"<!ENTITY\b",
        re.IGNORECASE,
    )

    XML_DOCTYPE_PATTERN = re.compile(
        r"<!DOCTYPE\b",
        re.IGNORECASE,
    )

    SVG_USE_PATTERN = re.compile(
        r"<\s*use\b",
        re.IGNORECASE,
    )

    STYLE_URL_PATTERN = re.compile(
        r"url\s*\(",
        re.IGNORECASE,
    )

    def __init__(
        self,
        config: ParserSecurityConfig | None = None,
    ) -> None:
        self.config = (
            config
            or ParserSecurityConfig()
        )

    def validate(
        self,
        source: str,
    ) -> list[SecurityFinding]:
        if not isinstance(
            source,
            str,
        ):
            raise TypeError(
                "Diagram parser input must be a string"
            )

        findings: list[
            SecurityFinding
        ] = []

        if len(source.encode("utf-8")) > (
            self.config.max_input_size
        ):
            findings.append(
                SecurityFinding(
                    code="INPUT_TOO_LARGE",
                    message=(
                        "Diagram input exceeds "
                        "the maximum allowed size."
                    ),
                )
            )

        lines = source.splitlines()

        if len(lines) > (
            self.config.max_lines
        ):
            findings.append(
                SecurityFinding(
                    code="TOO_MANY_LINES",
                    message=(
                        "Diagram contains too many lines."
                    ),
                )
            )

        for index, line in enumerate(
            lines,
            start=1,
        ):
            if len(line) > (
                self.config.max_line_length
            ):
                findings.append(
                    SecurityFinding(
                        code="LINE_TOO_LONG",
                        message=(
                            "Diagram contains a line "
                            "that exceeds the maximum "
                            "allowed length."
                        ),
                        line=index,
                    )
                )

        self._check_scripts(
            source,
            findings,
        )

        self._check_event_handlers(
            source,
            findings,
        )

        self._check_urls(
            source,
            findings,
        )

        self._check_xml_entities(
            source,
            findings,
        )

        return findings

    def enforce(
        self,
        source: str,
    ) -> str:
        findings = self.validate(
            source
        )

        errors = [
            finding
            for finding in findings
            if finding.severity
            in {
                "error",
                "critical",
            }
        ]

        if errors:
            raise ParserSecurityError(
                "Unsafe diagram input rejected.",
                errors,
            )

        return source

    def sanitize(
        self,
        source: str,
    ) -> str:
        """
        Best-effort sanitization.

        This should be used as a preprocessing step,
        but `enforce()` should still be used when strict
        security is required.
        """

        if not isinstance(
            source,
            str,
        ):
            raise TypeError(
                "Diagram parser input must be a string"
            )

        result = source

        if not self.config.allow_scripts:
            result = re.sub(
                r"<\s*script\b[^>]*>.*?<\s*/\s*script\s*>",
                "",
                result,
                flags=(
                    re.IGNORECASE
                    | re.DOTALL
                ),
            )

            result = re.sub(
                r"<\s*script\b[^>]*/?>",
                "",
                result,
                flags=re.IGNORECASE,
            )

        result = re.sub(
            r"\bon[a-z]+\s*=\s*(?:\"[^\"]*\"|'[^']*'|[^\s>]+)",
            "",
            result,
            flags=re.IGNORECASE,
        )

        result = re.sub(
            r"javascript\s*:",
            "",
            result,
            flags=re.IGNORECASE,
        )

        result = re.sub(
            r"vbscript\s*:",
            "",
            result,
            flags=re.IGNORECASE,
        )

        if not self.config.allow_data_urls:
            result = re.sub(
                r"data\s*:",
                "",
                result,
                flags=re.IGNORECASE,
            )

        # Prevent XML external entity declarations.
        result = re.sub(
            r"<!DOCTYPE[^>]*>",
            "",
            result,
            flags=(
                re.IGNORECASE
                | re.DOTALL
            ),
        )

        result = re.sub(
            r"<!ENTITY[^>]*>",
            "",
            result,
            flags=(
                re.IGNORECASE
                | re.DOTALL
            ),
        )

        return result

    def sanitize_html(
        self,
        source: str,
    ) -> str:
        """
        HTML-oriented sanitizer.

        This does not attempt to implement a complete HTML
        sanitizer; it removes the dangerous constructs relevant
        to diagram imports.
        """

        result = self.sanitize(
            source
        )

        if not self.config.allow_external_urls:
            result = self._remove_external_urls(
                result
            )

        result = re.sub(
            r"<\s*(iframe|object|embed|applet)\b[^>]*>.*?<\s*/\s*\1\s*>",
            "",
            result,
            flags=(
                re.IGNORECASE
                | re.DOTALL
            ),
        )

        result = re.sub(
            r"<\s*(iframe|object|embed|applet)\b[^>]*/?>",
            "",
            result,
            flags=re.IGNORECASE,
        )

        return result

    def escape_text(
        self,
        value: str,
    ) -> str:
        """
        Escape untrusted text for safe HTML rendering.
        """

        return html.escape(
            str(value),
            quote=True,
        )

    def _check_scripts(
        self,
        source: str,
        findings: list[
            SecurityFinding
        ],
    ) -> None:
        if (
            not self.config.allow_scripts
            and self.SCRIPT_PATTERN.search(
                source
            )
        ):
            findings.append(
                SecurityFinding(
                    code="SCRIPT",
                    message=(
                        "Embedded script content "
                        "is not allowed."
                    ),
                )
            )

    def _check_event_handlers(
        self,
        source: str,
        findings: list[
            SecurityFinding
        ],
    ) -> None:
        if self.EVENT_HANDLER_PATTERN.search(
            source
        ):
            findings.append(
                SecurityFinding(
                    code="EVENT_HANDLER",
                    message=(
                        "HTML event handlers "
                        "are not allowed."
                    ),
                )
            )

    def _check_urls(
        self,
        source: str,
        findings: list[
            SecurityFinding
        ],
    ) -> None:
        if self.JAVASCRIPT_URL_PATTERN.search(
            source
        ):
            findings.append(
                SecurityFinding(
                    code="SCRIPT_URL",
                    message=(
                        "JavaScript/VBScript URLs "
                        "are not allowed."
                    ),
                )
            )

        if (
            not self.config.allow_data_urls
            and self.DATA_URL_PATTERN.search(
                source
            )
        ):
            findings.append(
                SecurityFinding(
                    code="DATA_URL",
                    message=(
                        "Data URLs are not allowed."
                    ),
                )
            )

        if (
            not self.config.allow_external_urls
            and self.EXTERNAL_URL_PATTERN.search(
                source
            )
        ):
            findings.append(
                SecurityFinding(
                    code="EXTERNAL_URL",
                    message=(
                        "External URLs are not allowed "
                        "by the parser security policy."
                    ),
                    severity="warning",
                )
            )

    def _check_xml_entities(
        self,
        source: str,
        findings: list[
            SecurityFinding
        ],
    ) -> None:
        if self.XML_ENTITY_PATTERN.search(
            source
        ):
            findings.append(
                SecurityFinding(
                    code="XML_ENTITY",
                    message=(
                        "Custom XML entities are "
                        "not allowed."
                    ),
                )
            )

        if self.XML_DOCTYPE_PATTERN.search(
            source
        ):
            findings.append(
                SecurityFinding(
                    code="XML_DOCTYPE",
                    message=(
                        "XML DOCTYPE declarations "
                        "are not allowed."
                    ),
                )
            )

    def _remove_external_urls(
        self,
        source: str,
    ) -> str:
        return re.sub(
            r"https?://[^\s\"'<>)]+",
            "",
            source,
            flags=re.IGNORECASE,
        )


def validate_diagram_input(
    source: str,
    config: ParserSecurityConfig | None = None,
) -> None:
    """
    Convenience function for strict validation.
    """

    DiagramParserSecurity(
        config
    ).enforce(source)


def sanitize_diagram_input(
    source: str,
    config: ParserSecurityConfig | None = None,
) -> str:
    """
    Convenience function for sanitization.
    """

    return DiagramParserSecurity(
        config
    ).sanitize(source)