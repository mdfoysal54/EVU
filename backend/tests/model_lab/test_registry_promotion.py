from app.model_lab.registry.active import (
    ActiveModelPointer,
)
from app.model_lab.registry.promotion import (
    decide_promotion,
)


def test_promotion():
    decision = decide_promotion(
        "staging",
        "production",
        benchmark_score=0.9,
        pass_rate=0.9,
        safety_score=1.0,
        regression=0.0,
    )

    assert decision.approved is True


def test_active_pointer(tmp_path):
    pointer = ActiveModelPointer(
        tmp_path / "active.json"
    )

    pointer.set(
        "evu",
        "v1",
    )

    value = pointer.get()

    assert value == {
        "model_id": "evu",
        "version": "v1",
    }