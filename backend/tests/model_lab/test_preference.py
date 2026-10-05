import json

from app.model_lab.preference.schema import (
    PreferenceExample,
    load_preference_jsonl,
)


def test_preference_example_validation():
    example = PreferenceExample(
        prompt="Question",
        chosen="Good answer",
        rejected="Bad answer",
    )

    example.validate()

    assert example.prompt == "Question"
    assert example.chosen != example.rejected


def test_preference_jsonl_loader(tmp_path):
    path = tmp_path / "preferences.jsonl"

    path.write_text(
        json.dumps(
            {
                "prompt": "Hello",
                "chosen": "Hi!",
                "rejected": "Unknown.",
            }
        )
        + "\n",
        encoding="utf-8",
    )

    examples = load_preference_jsonl(
        path
    )

    assert len(examples) == 1
    assert examples[0].chosen == "Hi!"