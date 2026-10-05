from __future__ import annotations

from dataclasses import dataclass


@dataclass
class ValidationResult:
    valid: bool
    errors: list[str]


def validate_sft_record(
    record: dict,
) -> ValidationResult:
    errors: list[str] = []

    if not isinstance(record, dict):
        return ValidationResult(
            valid=False,
            errors=["record_not_object"],
        )

    if "messages" in record:
        messages = record["messages"]

        if not isinstance(messages, list):
            errors.append("messages_not_list")

        else:
            if not messages:
                errors.append("empty_messages")

            for index, message in enumerate(
                messages
            ):
                if not isinstance(
                    message,
                    dict,
                ):
                    errors.append(
                        f"message_{index}_not_object"
                    )
                    continue

                role = message.get("role")
                content = message.get("content")

                if role not in {
                    "system",
                    "user",
                    "assistant",
                    "tool",
                }:
                    errors.append(
                        f"message_{index}_invalid_role"
                    )

                if not isinstance(
                    content,
                    str,
                ) or not content.strip():
                    errors.append(
                        f"message_{index}_empty_content"
                    )

    else:
        prompt = record.get(
            "prompt",
            record.get("instruction"),
        )

        response = record.get(
            "response",
            record.get("output"),
        )

        if not isinstance(
            prompt,
            str,
        ) or not prompt.strip():
            errors.append("missing_prompt")

        if not isinstance(
            response,
            str,
        ) or not response.strip():
            errors.append("missing_response")

    return ValidationResult(
        valid=not errors,
        errors=errors,
    )