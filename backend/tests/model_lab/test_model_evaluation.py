from app.model_lab.evaluation.model_eval import (
    ModelEvaluation,
)


def test_model_evaluation():
    evaluation = ModelEvaluation(
        model_id="evu",
        version="1",
        benchmark_score=0.8,
        pass_rate=0.9,
        latency=0.5,
        safety_score=1.0,
    )

    assert (
        evaluation.deployment_score()
        > 0.8
    )