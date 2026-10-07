from app.model_lab.benchmark.schema import (
    BenchmarkReport,
    BenchmarkResult,
)
from app.model_lab.benchmark.regression import (
    compare_reports,
)


def test_regression_detection():
    current = BenchmarkReport(
        model_id="evu",
        model_version="1",
        results=[
            BenchmarkResult(
                case_id="1",
                category="reasoning",
                score=0.9,
                passed=True,
                latency_seconds=0.1,
            )
        ],
    )

    candidate = BenchmarkReport(
        model_id="evu",
        model_version="2",
        results=[
            BenchmarkResult(
                case_id="1",
                category="reasoning",
                score=0.7,
                passed=True,
                latency_seconds=0.1,
            )
        ],
    )

    result = compare_reports(
        current,
        candidate,
        max_category_drop=0.05,
    )

    assert result.acceptable is False
    assert "reasoning" in (
        result.regressions
    )