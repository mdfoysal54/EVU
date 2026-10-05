from __future__ import annotations


def detect_language(text: str) -> str:
    if not text.strip():
        return "unknown"

    bangla = 0
    latin = 0
    digits = 0
    other = 0

    for char in text:
        code = ord(char)

        if 0x0980 <= code <= 0x09FF:
            bangla += 1

        elif (
            "a" <= char.lower() <= "z"
        ):
            latin += 1

        elif char.isdigit():
            digits += 1

        elif char.isspace():
            continue

        else:
            other += 1

    meaningful = (
        bangla
        + latin
        + digits
        + other
    )

    if meaningful == 0:
        return "unknown"

    if bangla / meaningful >= 0.30:
        return "bn"

    if latin / meaningful >= 0.45:
        return "en"

    if bangla > latin:
        return "bn"

    if latin > 0:
        return "en"

    return "other"