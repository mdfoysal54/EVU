from app.model_lab.datasets.validation import (
    validate_sft_record,
)


def test_messages_record():
    result = validate_sft_record(
        {
            "messages": [
                {
                    "role": "user",
                    "content": "Hello",
                },
                {
                    "role": "assistant",
                    "content": "Hi.",
                },
            ]
        }
    )

    assert result.valid is True


def test_invalid_record():
    result = validate_sft_record(
        {
            "messages": [
                {
                    "role": "invalid",
                    "content": "",
                }
            ]
        }
    )

    assert result.valid is False