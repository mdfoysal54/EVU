from app.model_lab.datasets import (
    build_coding_dataset,
    build_reasoning_dataset,
)

from app.model_lab.experience import (
    ExperienceEvaluation,
    ExperienceRecord,
)


def make_experience(
    experience_id: str,
    task_type: str,
    prompt: str,
    response: str,
):

    return ExperienceRecord(
        experience_id=experience_id,
        created_at="2026-10-01T00:00:00+00:00",
        prompt=prompt,
        response=response,
        task_type=task_type,
        success=True,
        evaluation=ExperienceEvaluation(
            correctness=0.9,
            usefulness=0.9,
            safety=1.0,
            tool_success=1.0,
            overall=0.92,
            passed=True,
        ),
    )


def test_reasoning_dataset():

    examples = build_reasoning_dataset(
        [
            make_experience(
                "reason-1",
                "reasoning",
                "Why does 2 + 2 equal 4?",
                "Because adding two pairs gives four items.",
            )
        ]
    )

    assert len(examples) == 1
    assert examples[0].reasoning_type == "reasoning"


def test_coding_dataset():

    examples = build_coding_dataset(
        [
            make_experience(
                "code-1",
                "coding",
                "Write a Python function that adds two numbers.",
                "def add(a, b):\n    return a + b",
            )
        ]
    )

    assert len(examples) == 1
    assert examples[0].language == "python"