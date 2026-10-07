from __future__ import annotations

import json
from pathlib import Path

from .schema import (
    ImprovementCandidate,
)


def load_experiences(
    path: str | Path,
) -> list[dict]:
    path = Path(path)

    if not path.exists():
        return []

    records = []

    with path.open(
        "r",
        encoding="utf-8",
    ) as handle:
        for line in handle:
            line = line.strip()

            if line:
                records.append(
                    json.loads(line)
                )

    return records


def extract_candidates(
    records: list[dict],
) -> list[ImprovementCandidate]:
    candidates = []

    for index, record in enumerate(
        records
    ):
        prompt = str(
            record.get(
                "prompt",
                "",
            )
        )

        response = str(
            record.get(
                "response",
                record.get(
                    "answer",
                    "",
                ),
            )
        )

        if not prompt or not response:
            continue

        evaluation = record.get("evaluation") or {}
        if not isinstance(evaluation, dict):
            evaluation = {}

        raw_score = evaluation.get(
            "score",
            record.get(
                "quality_score",
                0.0,
            ),
        )

        try:
            score = float(raw_score) if raw_score is not None else 0.0
        except (ValueError, TypeError):
            score = 0.0

        success = bool(
            record.get(
                "success",
                True,
            )
        )

        raw_metadata = record.get("metadata")
        metadata = dict(raw_metadata) if isinstance(raw_metadata, dict) else {}

        candidates.append(
            ImprovementCandidate(
                example_id=str(
                    record.get(
                        "id",
                        index,
                    )
                ),
                prompt=prompt,
                response=response,
                task_type=str(
                    record.get(
                        "task_type",
                        "general",
                    )
                ),
                quality_score=score,
                success=success,
                metadata=metadata,
            )
        )

    return candidates