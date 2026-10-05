from __future__ import annotations

from dataclasses import asdict, dataclass, field
import json
from pathlib import Path
from typing import Any, Iterable


@dataclass
class PreferenceExample:
    """
    One preference-training example.

    prompt:
        The user/task instruction.

    chosen:
        The response preferred by the evaluator/human.

    rejected:
        The response considered worse.

    metadata:
        Optional provenance information.
    """

    prompt: str
    chosen: str
    rejected: str
    metadata: dict[str, Any] = field(default_factory=dict)

    def validate(self) -> None:
        if not self.prompt.strip():
            raise ValueError("Preference prompt cannot be empty.")

        if not self.chosen.strip():
            raise ValueError("Chosen response cannot be empty.")

        if not self.rejected.strip():
            raise ValueError("Rejected response cannot be empty.")

        if self.chosen.strip() == self.rejected.strip():
            raise ValueError("Chosen and rejected responses must differ.")

    def to_dict(self) -> dict[str, Any]:
        self.validate()
        return asdict(self)


def load_preference_jsonl(
    path: str | Path,
) -> list[PreferenceExample]:
    """
    Load preference examples from JSONL.

    Expected format:
    {
        "prompt": "...",
        "chosen": "...",
        "rejected": "...",
        "metadata": {}
    }
    """
    path = Path(path)

    if not path.exists():
        raise FileNotFoundError(
            f"Preference dataset not found: {path}"
        )

    examples: list[PreferenceExample] = []

    with path.open("r", encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            line = line.strip()

            if not line:
                continue

            try:
                payload = json.loads(line)
            except json.JSONDecodeError as exc:
                raise ValueError(
                    f"Invalid JSON on line {line_number}: {exc}"
                ) from exc

            example = PreferenceExample(
                prompt=str(payload.get("prompt", "")),
                chosen=str(payload.get("chosen", "")),
                rejected=str(payload.get("rejected", "")),
                metadata=dict(payload.get("metadata") or {}),
            )

            try:
                example.validate()
            except ValueError as exc:
                raise ValueError(
                    f"Invalid preference example on line {line_number}: {exc}"
                ) from exc

            examples.append(example)

    if not examples:
        raise ValueError(f"No preference examples found in {path}")

    return examples


def save_preference_jsonl(
    examples: Iterable[PreferenceExample],
    path: str | Path,
) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open("w", encoding="utf-8") as handle:
        for example in examples:
            handle.write(
                json.dumps(
                    example.to_dict(),
                    ensure_ascii=False,
                )
                + "\n"
            )