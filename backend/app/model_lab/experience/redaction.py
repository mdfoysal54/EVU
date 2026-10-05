from __future__ import annotations

import re
from typing import Any

SENSITIVE_KEYS = {
    "password",
    "passwd",
    "secret",
    "api_key",
    "apikey",
    "access_token",
    "refresh_token",
    "authorization",
    "cookie",
    "session",
    "private_key",
    "client_secret",
}

SENSITIVE_PATTERNS = [
    re.compile(r"(?i)(authorization\s*[:=]\s*(?:bearer\s+)?)[^\s,]+"),
    re.compile(r"(?i)(bearer\s+)[A-Za-z0-9._-]+"),
    re.compile(r"(?i)(api[_-]?key\s*[:=]\s*)[^\s,]+"),
]


def redact_text(value: str) -> str:
    result = value
    for pattern in SENSITIVE_PATTERNS:
        result = pattern.sub(r"\1[REDACTED]", result)
    return result


def redact(value: Any) -> Any:
    if isinstance(value, str):
        return redact_text(value)

    if isinstance(value, list):
        return [redact(item) for item in value]

    if isinstance(value, tuple):
        return tuple(redact(item) for item in value)

    if isinstance(value, dict):
        output = {}
        for key, item in value.items():
            normalized = str(key).lower()
            if normalized in SENSITIVE_KEYS:
                output[key] = "[REDACTED]"
            else:
                output[key] = redact(item)
        return output

    return value