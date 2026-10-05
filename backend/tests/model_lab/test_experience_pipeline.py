from pathlib import Path

from app.model_lab.experience import (
    ExperienceEvaluator,
    ExperiencePipeline,
    ExperienceRecord,
    ExperienceStore,
)


def make_experience(
    experience_id: str,
    prompt: str,
    response: str,
    success: bool = True,
):
    return ExperienceRecord(
        experience_id=experience_id,
        created_at="2026-01-01T00:00:00+00:00",
        prompt=prompt,
        response=response,
        model="evu",
        provider="evu",
        task_type="general",
        success=success,
    )


def test_pipeline_accepts_good_experience(
    tmp_path: Path,
):

    store = ExperienceStore(
        tmp_path / "experiences.jsonl"
    )

    evaluator = ExperienceEvaluator(
        minimum_overall=0.70
    )

    pipeline = ExperiencePipeline(
        store,
        evaluator,
    )

    experience = make_experience(
        "exp-good",
        "Explain Python.",
        (
            "Python is a high-level programming "
            "language commonly used for web development, "
            "automation, data analysis and machine learning."
        ),
    )

    pipeline.record(experience)

    assert experience.evaluation is not None
    assert experience.evaluation.passed is True


def test_pipeline_rejects_failed_experience(
    tmp_path: Path,
):

    store = ExperienceStore(
        tmp_path / "experiences.jsonl"
    )

    pipeline = ExperiencePipeline(
        store,
        ExperienceEvaluator(),
    )

    experience = make_experience(
        "exp-bad",
        "Explain Python.",
        "",
        success=False,
    )

    pipeline.record(experience)

    assert experience.evaluation is not None
    assert experience.evaluation.passed is False


def test_build_sft_dataset(
    tmp_path: Path,
):

    store = ExperienceStore(
        tmp_path / "experiences.jsonl"
    )

    pipeline = ExperiencePipeline(
        store,
        ExperienceEvaluator(),
    )

    experience = make_experience(
        "exp-sft",
        "What is 2 + 2?",
        "2 + 2 equals 4.",
    )

    pipeline.record(experience)

    result = pipeline.build_datasets()

    assert result.total_experiences == 1
    assert result.accepted_experiences == 1
    assert len(result.sft_examples) == 1