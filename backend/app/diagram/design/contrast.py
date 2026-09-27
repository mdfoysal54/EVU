import re

def _srgb_to_linear(c: float) -> float:
    c = c / 255.0
    return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4

def relative_luminance(hex_color: str) -> float:
    clean_hex = hex_color.lstrip("#")
    if len(clean_hex) == 3:
        clean_hex = "".join([c * 2 for c in clean_hex])
    r, g, b = [int(clean_hex[i:i+2], 16) for i in (0, 2, 4)]
    return 0.2126 * _srgb_to_linear(r) + 0.7152 * _srgb_to_linear(g) + 0.0722 * _srgb_to_linear(b)

def contrast_ratio(foreground: str, background: str) -> float:
    lum1 = relative_luminance(foreground)
    lum2 = relative_luminance(background)
    brightest = max(lum1, lum2)
    darkest = min(lum1, lum2)
    return (brightest + 0.05) / (darkest + 0.05)

def passes_wcag_aa(foreground: str, background: str) -> bool:
    return contrast_ratio(foreground, background) >= 4.5