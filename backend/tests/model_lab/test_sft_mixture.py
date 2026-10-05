from app.model_lab.sft.mixture import (
    mix_specialized,
)


def test_mixture():
    records = mix_specialized(
        [
            {
                "prompt": "reason",
                "response": "answer",
            }
        ],
        [
            {
                "prompt": "code",
                "response": "print(1)",
            }
        ],
        [
            {
                "prompt": "use tool",
                "response": "tool",
            }
        ],
    )

    assert len(records) == 3

    task_types = {
        record["task_type"]
        for record in records
    }

    assert task_types == {
        "reasoning",
        "coding",
        "tool_use",
    }