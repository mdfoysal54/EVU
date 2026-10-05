from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Iterable

from .pairs import (
    PreferencePair,
    make_pair,
)
from .scoring import score_candidate


@dataclass
class Candidate:
    text: str
    metadata: dict


@dataclass
class GeneratedPreference:
    prompt: str
    candidates: list[Candidate]
    pair: PreferencePair | None


def generate_candidates(
    prompt: str,
    generator: Callable[
        [str],
        str,
    ],
    count: int = 2,
) -> list[Candidate]:
    if count < 2:
        raise ValueError(
            "count must be >= 2"
        )

    result = []

    for index in range(count):
        text = generator(prompt)

        result.append(
            Candidate(
                text=text,
                metadata={
                    "candidate_index": index,
                },
            )
        )

    return result


def choose_pair(
    prompt: str,
    candidates: list[Candidate],
    *,
    min_margin: float = 0.05,
) -> PreferencePair | None:
    if len(candidates) < 2:
        return None

    scored = [
        score_candidate(
            prompt,
            candidate.text,
        )
        for candidate in candidates
    ]

    best = max(
        scored,
        key=lambda item: item.score,
    )

    worst = min(
        scored,
        key=lambda item: item.score,
    )

    return make_pair(
        prompt,
        best.response,
        worst.response,
        best.score,
        worst.score,
        min_margin=min_margin,
    )


def build_preferences(
    prompts: Iterable[str],
    generator: Callable[
        [str],
        str,
    ],
    *,
    candidates_per_prompt: int = 2,
    min_margin: float = 0.05,
) -> list[PreferencePair]:
    pairs = []

    for prompt in prompts:
        candidates = generate_candidates(
            prompt,
            generator,
            candidates=candidates_per_prompt,
        )

        pair = choose_pair(
            prompt,
            candidates,
            min_margin=min_margin,
        )

        if pair is not None:
            pairs.append(pair)

    return pairs