from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass
class DatasetExample:
    """
    Common training example format.
    """

    example_id: str

    category: str

    prompt: str

    response: str

    task_type: str

    quality_score: float

    metadata: dict[str, Any] = field(
        default_factory=dict
    )

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class ReasoningExample:
    example_id: str

    prompt: str

    answer: str

    reasoning_type: str

    quality_score: float

    metadata: dict[str, Any] = field(
        default_factory=dict
    )

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class CodingExample:
    example_id: str

    prompt: str

    response: str

    language: str

    task_type: str

    quality_score: float

    metadata: dict[str, Any] = field(
        default_factory=dict
    )

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class ToolUseExample:
    example_id: str

    prompt: str

    response: str

    tool_name: str

    tool_arguments: dict[str, Any]

    tool_result: Any

    tool_success: bool

    quality_score: float

    metadata: dict[str, Any] = field(
        default_factory=dict
    )

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)