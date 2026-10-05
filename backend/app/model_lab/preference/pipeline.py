from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from .export import (
    write_preference_jsonl,
)
from .generation import (
    build_preferences,
)


@dataclass
class PreferenceGenerationResult:
    prompts: int
    pairs: int
    output_path: str


class PreferenceGenerationPipeline:
    def __init__(
        self,
        generator: Callable[
            [str],
            str,
        ],
    ) -> None:
        self.generator = generator

    def run(
        self,
        prompts: list[str],
        output_path: str,
        *,
        candidates_per_prompt: int = 2,
        min_margin: float = 0.05,
    ) -> PreferenceGenerationResult:
        pairs = build_preferences(
            prompts,
            self.generator,
            candidates_per_prompt=(
                candidates_per_prompt
            ),
            min_margin=min_margin,
        )

        write_preference_jsonl(
            pairs,
            output_path,
        )

        return PreferenceGenerationResult(
            prompts=len(prompts),
            pairs=len(pairs),
            output_path=output_path,
        )