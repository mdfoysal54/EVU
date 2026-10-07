from app.model_lab.benchmark.schema import (
    BenchmarkCase,
)
from app.model_lab.benchmark.runner import (
    BenchmarkRunner,
)
from app.model_lab.benchmark.scorers import (
    exact_match,
)


def test_benchmark_runner():
    cases = [
        BenchmarkCase(
            case_id="1",
            category="general",
            prompt="2+2",
            expected="4",
        )
    ]

    runner = BenchmarkRunner(
        threshold=0.5
    )

    results = runner.run(
        cases,
        lambda prompt: "4",
        exact_match,
    )

    assert len(results) == 1
    assert results[0].passed is True
    assert results[0].score == 1.0