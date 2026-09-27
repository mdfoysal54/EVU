from datetime import datetime, timezone
import math


def recency_score(
    created_at: datetime,
    *,
    half_life_days: float = 30.0,
) -> float:

    now = datetime.now(timezone.utc)

    if created_at.tzinfo is None:
        created_at = created_at.replace(
            tzinfo=timezone.utc
        )

    age_seconds = max(
        0.0,
        (now - created_at).total_seconds(),
    )

    age_days = age_seconds / 86400.0

    return math.exp(
        -math.log(2)
        * age_days
        / half_life_days
    )