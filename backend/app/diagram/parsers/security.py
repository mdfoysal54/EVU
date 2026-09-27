import html
import re

INJECTION_PATTERNS = [
    re.compile(r"ignore\s+(all\s+)?(previous|prior)\s+instructions", re.IGNORECASE),
    re.compile(r"system\s*prompt", re.IGNORECASE),
    re.compile(r"expose\s+(api\s+keys|secrets|passwords)", re.IGNORECASE),
]

def sanitize_label(text: str) -> str:
    """Escapes HTML entities and defangs potential prompt injections."""
    sanitized = html.escape(text.strip())
    for pattern in INJECTION_PATTERNS:
        sanitized = pattern.sub("[DEFANGED_PROMPT_INJECTION]", sanitized)
    return sanitized