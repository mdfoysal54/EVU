from app.model_lab.evaluation.quality import (
    score_instruction,
)


def test_good_instruction_scores():
    result = score_instruction(
        "Explain what Python is.",
        (
            "Python is a general-purpose "
            "programming language."
        ),
    )

    assert result.score > 0.0
    assert result.accepted is True


def test_empty_response_rejected():
    result = score_instruction(
        "Explain Python.",
        "",
    )

    assert result.accepted is False


def test_identical_instruction_response():
    result = score_instruction(
        "Explain Python.",
        "Explain Python.",
    )

    assert result.score < 0.65