from __future__ import annotations

import json
from pathlib import Path

from .schema import (
    BenchmarkReport,
    BenchmarkResult,
)


def build_report(
    model_id: str,
    model_version: str,
    results: list[BenchmarkResult],
) -> BenchmarkReport:
    return BenchmarkReport(
        model_id=model_id,
        model_version=model_version,
        results=results,
    )


def save_report(
    report: BenchmarkReport,
    path: str | Path,
) -> None:
    path = Path(path)

    path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    path.write_text(
        json.dumps(
            report.to_dict(),
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )