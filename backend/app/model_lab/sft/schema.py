from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Iterable


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
            # Fallback to prompt/response if provided in flat format
            if "prompt" in data and "response" in data:
                return cls(
                    messages=[
                        Message(role="user", content=str(data["prompt"])),
                        Message(role="assistant", content=str(data["response"])),
                    ],
                    metadata=data.get("metadata"),
                )
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


@dataclass
class SFTExample:
    """
    Representation of an SFT training instance, supporting flat prompt/response
    as well as underlying conversational message structures.
    """
    prompt: str = ""
    response: str = ""
    task_type: str = "general"
    metadata: dict[str, Any] = field(default_factory=dict)
    messages: list[Message] = field(default_factory=list)

    def __post_init__(self) -> None:
        # Synchronize messages and prompt/response
        if not self.messages and self.prompt and self.response:
            self.messages = [
                Message(role="user", content=self.prompt),
                Message(role="assistant", content=self.response),
            ]
        elif self.messages:
            if not self.response and self.messages[-1].role == "assistant":
                self.response = self.messages[-1].content
            if not self.prompt:
                user_msgs = [m.content for m in self.messages if m.role == "user"]
                if user_msgs:
                    self.prompt = user_msgs[0]

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "SFTExample":
        metadata = data.get("metadata") or {}
        task_type = data.get("task_type", metadata.get("task_type", "general"))

        if "messages" in data:
            messages = [
                Message(role=item["role"], content=item["content"])
                for item in data["messages"]
            ]
            user_text = next((m.content for m in messages if m.role == "user"), "")
            asst_text = next((m.content for m in reversed(messages) if m.role == "assistant"), "")
            return cls(
                prompt=data.get("prompt", user_text),
                response=data.get("response", asst_text),
                task_type=task_type,
                metadata=metadata,
                messages=messages,
            )

        return cls(
            prompt=str(data.get("prompt", "")),
            response=str(data.get("response", "")),
            task_type=task_type,
            metadata=metadata,
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "prompt": self.prompt,
            "response": self.response,
            "task_type": self.task_type,
            "metadata": self.metadata,
            "messages": [asdict(m) for m in self.messages] if self.messages else [],
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
    examples: Iterable[ConversationExample | SFTExample],
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


__all__ = [
    "VALID_ROLES",
    "Message",
    "ConversationExample",
    "SFTExample",
    "load_jsonl_examples",
    "save_jsonl_examples",
]