from pathlib import Path

from app.model_lab.experience import (
    ExperienceRecorder,
    ExperienceStore,
)

from app.model_lab.runtime import (
    record_request,
    record_tool_start,
    record_tool_result,
)


def test_runtime_recording(
    tmp_path: Path,
):

    store = ExperienceStore(
        tmp_path / "runtime.jsonl"
    )

    recorder = ExperienceRecorder(
        store
    )

    with record_request(
        recorder=recorder,
        prompt="Search for Python documentation.",
        model="evu",
        provider="evu",
        task_type="research",
    ) as session:

        step_id = record_tool_start(
            "web_search",
            {
                "query":
                    "Python documentation"
            },
        )

        record_tool_result(
            step_id,
            {
                "results": [
                    "Python docs"
                ]
            },
            success=True,
        )

        session.model_response(
            "The Python documentation is available online."
        )

        experience = session.finish(
            success=True
        )

    assert experience.success is True
    assert len(experience.steps) == 1

    records = store.load_all()

    assert len(records) == 1
    assert records[0].prompt.startswith(
        "Search"
    )


def test_redaction(
    tmp_path: Path,
):

    store = ExperienceStore(
        tmp_path / "runtime.jsonl"
    )

    recorder = ExperienceRecorder(
        store
    )

    session = recorder.start(
        prompt=(
            "Use api_key=SUPER_SECRET_VALUE"
        )
    )

    session.model_response(
        "authorization: Bearer SECRET123"
    )

    experience = session.finish()

    assert "SUPER_SECRET_VALUE" not in (
        experience.prompt
    )

    assert "SECRET123" not in (
        experience.response
    )