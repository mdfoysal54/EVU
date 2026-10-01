from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Sequence


@dataclass(frozen=True)
class SummaryResult:
    summary: str
    source_count: int
    method: str


class MemorySummarizer:
    """LLM-compatible summarizer with deterministic fallback."""

    def __init__(
        self,
        model: Callable[[str], str] | None = None,
        max_chars: int = 1200,
    ) -> None:
        self.model = model
        self.max_chars = max(
            100,
            max_chars,
        )

    def summarize(
        self,
        texts: Sequence[str],
        instruction: str | None = None,
    ) -> SummaryResult:
        cleaned = [
            text.strip()
            for text in texts
            if text and text.strip()
        ]

        if not cleaned:
            return SummaryResult(
                "",
                0,
                "empty",
            )

        prompt = (
            instruction
            or (
                "Summarize the following memory "
                "items faithfully, preserving "
                "concrete facts and uncertainty."
            )
        )

        joined = (
            "\n\n---\n\n".join(cleaned)
        )

        if self.model:
            try:
                result = self.model(
                    f"{prompt}\n\n{joined}"
                )

                if result and result.strip():
                    return SummaryResult(
                        result.strip()[
                            : self.max_chars
                        ],
                        len(cleaned),
                        "model",
                    )
            except Exception:
                pass

        summary = " ".join(cleaned)

        return SummaryResult(
            summary[: self.max_chars],
            len(cleaned),
            "extractive",
        )