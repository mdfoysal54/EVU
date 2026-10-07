from __future__ import annotations

import math
import re
from typing import Any


def _normalize(value: Any) -> str:
    return " ".join(
        str(value)
        .strip()
        .lower()
        .split()
    )


def exact_match(
    actual: Any,
    expected: Any,
) -> float:
    return float(
        _normalize(actual)
        == _normalize(expected)
    )


def contains_match(
    actual: Any,
    expected: Any,
) -> float:
    actual_text = _normalize(actual)
    expected_text = _normalize(expected)

    if not expected_text:
        return 0.0

    return float(
        expected_text in actual_text
    )


def numeric_match(
    actual: Any,
    expected: Any,
    tolerance: float = 1e-6,
) -> float:
    try:
        actual_number = float(
            re.sub(
                r"[^0-9eE+.\-]",
                "",
                str(actual),
            )
        )

        expected_number = float(
            re.sub(
                r"[^0-9eE+.\-]",
                "",
                str(expected),
            )
        )

    except (TypeError, ValueError):
        return 0.0

    if math.isclose(
        actual_number,
        expected_number,
        rel_tol=tolerance,
        abs_tol=tolerance,
    ):
        return 1.0

    return 0.0