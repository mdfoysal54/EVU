from app.model_lab.evaluation.suite import (
    EvaluationCase,
    EvaluationSuite,
)


def test_evaluation_suite():
    suite = EvaluationSuite(
        "test",
        threshold=0.5,
    )

    suite.add(
        EvaluationCase(
            name="case_1",
            prompt="hello",
            expected="hello",
        )
    )

    results = suite.run(
        lambda prompt: "hello",
        lambda case, output: (
            1.0
            if output == case.expected
            else 0.0
        ),
    )

    assert len(results) == 1
    assert results[0].passed is True