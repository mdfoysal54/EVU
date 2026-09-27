def reinforce(
    confidence: float,
    count: int,
    *,
    strength: float = 0.08,
) -> float:

    confidence = max(
        0.0,
        min(1.0, confidence),
    )

    return min(
        1.0,
        confidence
        + strength * (1.0 - confidence),
    )