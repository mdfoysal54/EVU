from app.model_lab.registry.gates import (
    evaluate_gate,
)


def test_gate_passes():
    result = evaluate_gate(
        benchmark_score=0.9,
        pass_rate=0.9,
        safety_score=1.0,
        regression=0.0,
    )

    assert result.passed is True


def test_gate_rejects_bad_model():
    result = evaluate_gate(
        benchmark_score=0.4,
        pass_rate=0.5,
        safety_score=0.5,
        regression=0.1,
    )

    assert result.passed is False
    assert result.reasons