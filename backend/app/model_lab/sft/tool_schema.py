from __future__ import annotations

from dataclasses import dataclass, asdict


@dataclass
class ToolCallExample:
    prompt: str
    tool_name: str
    arguments: dict
    observation: str
    final_response: str

    def to_record(self) -> dict:
        return {
            "prompt": self.prompt,
            "tool_name": self.tool_name,
            "arguments": self.arguments,
            "observation": self.observation,
            "response": self.final_response,
            "task_type": "tool_use",
        }


def format_tool_training_prompt(
    example: ToolCallExample,
) -> str:
    return (
        f"User:\n"
        f"{example.prompt}\n\n"
        f"Available tool:\n"
        f"{example.tool_name}\n\n"
        f"Arguments:\n"
        f"{example.arguments}\n\n"
        f"Tool observation:\n"
        f"{example.observation}\n\n"
        f"Assistant:"
    )