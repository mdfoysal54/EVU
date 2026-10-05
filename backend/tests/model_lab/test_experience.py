from pathlib import Path

from app.model_lab.experience import (
    ExperienceRecord,
    ExperienceStep,
    ExperienceStore,
)


def test_experience_roundtrip(tmp_path: Path):

    store = ExperienceStore(
        tmp_path / "experiences.jsonl"
    )

    experience = ExperienceRecord(
        experience_id="exp-001",
        created_at="2026-01-01T00:00:00+00:00",
        prompt="What is Python?",
        response="Python is a programming language.",
        model="evu",
        provider="evu",
        task_type="general",
        steps=[
            ExperienceStep(
                step_id=1,
                action="answer",
                observation="completed",
            )
        ],
    )

    store.append(experience)

    records = store.load_all()

    assert len(records) == 1
    assert records[0].experience_id == "exp-001"
    assert records[0].prompt == "What is Python?"
    assert records[0].response != ""