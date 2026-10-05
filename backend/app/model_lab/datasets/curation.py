from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from .quality_v2 import (
    CuratedRecord,
    evaluate_record,
)
from .dedup import deduplicate_records


@dataclass
class CurationResult:
    accepted: list[dict]
    rejected: list[dict]
    statistics: dict


def curate(
    records: Iterable[dict],
) -> CurationResult:
    records = deduplicate_records(
        records
    )

    accepted: list[dict] = []
    rejected: list[dict] = []

    reason_counts: dict[str, int] = {}

    for record in records:
        result: CuratedRecord = (
            evaluate_record(record)
        )

        enriched = dict(result.record)

        enriched["_quality"] = {
            "score": result.score,
            "language": result.language,
            "accepted": result.accepted,
            "reasons": result.reasons,
        }

        if result.accepted:
            accepted.append(enriched)
        else:
            rejected.append(enriched)

            for reason in result.reasons:
                reason_counts[reason] = (
                    reason_counts.get(
                        reason,
                        0,
                    )
                    + 1
                )

    total = (
        len(accepted)
        + len(rejected)
    )

    return CurationResult(
        accepted=accepted,
        rejected=rejected,
        statistics={
            "input_after_dedup": total,
            "accepted": len(accepted),
            "rejected": len(rejected),
            "acceptance_rate": (
                len(accepted) / total
                if total
                else 0.0
            ),
            "rejection_reasons": reason_counts,
        },
    )