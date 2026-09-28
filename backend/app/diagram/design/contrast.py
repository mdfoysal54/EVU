from __future__ import annotations


def _hex_to_rgb(value: str) -> tuple[int, int, int]:
    value = value.strip().lstrip("#")

    if len(value) != 6:
        raise ValueError(
            f"Invalid color: {value}"
        )

    return (
        int(value[0:2], 16),
        int(value[2:4], 16),
        int(value[4:6], 16),
    )


def relative_luminance(color: str) -> float:
    rgb = _hex_to_rgb(color)

    channels = []

    for value in rgb:
        channel = value / 255

        if channel <= 0.03928:
            channel /= 12.92
        else:
            channel = (
                (channel + 0.055) / 1.055
            ) ** 2.4

        channels.append(channel)

    return (
        0.2126 * channels[0]
        + 0.7152 * channels[1]
        + 0.0722 * channels[2]
    )


def contrast_ratio(
    foreground: str,
    background: str,
) -> float:

    first = relative_luminance(foreground)
    second = relative_luminance(background)

    lighter = max(first, second)
    darker = min(first, second)

    return (lighter + 0.05) / (darker + 0.05)


def passes_wcag_aa(
    foreground: str,
    background: str,
    *,
    large_text: bool = False,
) -> bool:

    ratio = contrast_ratio(
        foreground,
        background,
    )

    required = 3.0 if large_text else 4.5

    return ratio >= required