from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .sanitizer import DiagramSanitizer


class SourceTrust(str, Enum):
    TRUSTED = "trusted"
    USER = "user"
    EXTERNAL = "external"
    MODEL = "model"
    UNKNOWN = "unknown"


@dataclass(frozen=True)
class UntrustedSource:
    source_type: SourceTrust
    origin: str | None = None
    sanitized: bool = False


class UntrustedSourceGuard:
    """
    Central policy point for external/model-generated diagram content.
    """

    def __init__(
        self,
        sanitizer: DiagramSanitizer | None = None,
    ) -> None:

        self.sanitizer = (
            sanitizer or DiagramSanitizer()
        )

    def prepare_text(
        self,
        value: str,
        source: UntrustedSource,
    ) -> str:

        if source.source_type == SourceTrust.TRUSTED:
            return value

        return self.sanitizer.sanitize_text(
            value
        )

    def prepare_svg(
        self,
        svg: str,
        source: UntrustedSource,
    ) -> str:

        if source.source_type == SourceTrust.TRUSTED:
            return svg

        return self.sanitizer.sanitize_svg(
            svg
        )


def external_source(
    origin: str | None = None,
) -> UntrustedSource:

    return UntrustedSource(
        source_type=SourceTrust.EXTERNAL,
        origin=origin,
        sanitized=False,
    )


def model_source(
    origin: str | None = None,
) -> UntrustedSource:

    return UntrustedSource(
        source_type=SourceTrust.MODEL,
        origin=origin,
        sanitized=False,
    )