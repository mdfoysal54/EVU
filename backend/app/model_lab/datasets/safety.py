from __future__ import annotations

import re


_PATTERNS = (
    re.compile(
        r"\b(?:steal|dump|exfiltrate)\b.*"
        r"\bpasswords?\b",
        re.I,
    ),
    re.compile(
        r"\bmalware\s+payload\b",
        re.I,
    ),
    re.compile(
        r"\bransomware\s+deployment\b",
        re.I,
    ),
)


def safety_flags(text: str) -> list[str]:
    flags: list[str] = []

    for pattern in _PATTERNS:
        if pattern.search(text):
            flags.append(
                pattern.pattern
            )

    return flags


def is_safe_training_example(
    text: str,
) -> bool:
    return not safety_flags(text)