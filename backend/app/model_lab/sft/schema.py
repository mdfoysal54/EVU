from __future__ import annotations

from dataclasses import asdict, dataclass
import json
from pathlib import Path
from typing import Iterable


VALID_ROLES = {
    "system",
    "user",
    "assistant",
    "tool",
}


@dataclass
class Message:
    role: str
    content: str

    def __post_init__(self) -> None:
        self.role = str(self.role).strip().lower()

        if self.role not in VALID_ROLES:
            raise ValueError(
                f"Unsupported message role: {self.role}"
            )

        if not isinstance(self.content, str):
            raise TypeError(
                "Message content must be a string."
            )

        if not self.content.strip():
            raise ValueError(
                "Message content cannot be empty."
            )


@dataclass
class ConversationExample:
    messages: list[Message]
    metadata: dict | None = None

    def __post_init__(self) -> None:
        if not self.messages:
            raise ValueError(
                "A conversation must contain at least one message."
            )

        if self.messages[-1].role != "assistant":
            raise ValueError(
                "An SFT example must end with an assistant message."
            )

    @classmethod
    def from_dict(
        cls,
        data: dict,
    ) -> "ConversationExample":

        if "messages" not in data:
            raise ValueError(
                "SFT example is missing 'messages'."
            )

        messages = [
            Message(
                role=item["role"],
                content=item["content"],
            )
            for item in data["messages"]
        ]

        return cls(
            messages=messages,
            metadata=data.get("metadata"),
        )

    def to_dict(self) -> dict:
        return {
            "messages": [
                asdict(message)
                for message in self.messages
            ],
            "metadata": self.metadata or {},
        }


def load_jsonl_examples(
    path: str | Path,
) -> list[ConversationExample]:

    path = Path(path)

    if not path.exists():
        raise FileNotFoundError(
            f"SFT dataset does not exist: {path}"
        )

    examples: list[ConversationExample] = []

    with path.open(
        "r",
        encoding="utf-8",
    ) as handle:

        for line_number, line in enumerate(
            handle,
            start=1,
        ):
            line = line.strip()

            if not line:
                continue

            try:
                data = json.loads(line)

                examples.append(
                    ConversationExample.from_dict(
                        data
                    )
                )

            except Exception as exc:
                raise ValueError(
                    f"Invalid SFT example at "
                    f"{path}:{line_number}: {exc}"
                ) from exc

    if not examples:
        raise ValueError(
            f"No SFT examples found in {path}"
        )

    return examples


def save_jsonl_examples(
    examples: Iterable[ConversationExample],
    path: str | Path,
) -> None:

    path = Path(path)
    path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with path.open(
        "w",
        encoding="utf-8",
    ) as handle:

        for example in examples:
            handle.write(
                json.dumps(
                    example.to_dict(),
                    ensure_ascii=False,
                )
                + "\n"
            )