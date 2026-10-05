from __future__ import annotations

import re

from app.model_lab.experience.schema import (
    ExperienceRecord,
)

from .schema import CodingExample


CODING_TYPES = {
    "coding",
    "programming",
    "software_engineering",
    "debugging",
    "code_generation",
    "code_review",
}


LANGUAGE_PATTERNS = {
    "python": re.compile(
        r"(?i)\b(python|def |import |from .+ import )\b"
    ),
    "javascript": re.compile(
        r"(?i)\b(javascript|typescript|node\.js|const |let |function )\b"
    ),
    "java": re.compile(
        r"(?i)\b(java|public static void|System\.out)\b"
    ),
    "c++": re.compile(
        r"(?i)\b(c\+\+|std::|#include\s*<)\b"
    ),
    "rust": re.compile(
        r"(?i)\b(rust|fn main|let mut|cargo)\b"
    ),
    "go": re.compile(
        r"(?i)\b(golang|go language|package main|func main)\b"
    ),
}


def detect_language(
    text: str,
) -> str:

    for language, pattern in LANGUAGE_PATTERNS.items():

        if pattern.search(text):
            return language

    return "unknown"


def build_coding_dataset(
    experiences: list[ExperienceRecord],
    minimum_score: float = 0.75,
) -> list[CodingExample]:

    output = []

    for experience in experiences:

        if experience.task_type not in CODING_TYPES:
            continue

        if not experience.evaluation:
            continue

        score = (
            experience.evaluation.overall
        )

        if score < minimum_score:
            continue

        language = detect_language(
            experience.prompt
            + "\n"
            + experience.response
        )

        output.append(
            CodingExample(
                example_id=experience.experience_id,
                prompt=experience.prompt,
                response=experience.response,
                language=language,
                task_type=experience.task_type,
                quality_score=score,
                metadata={
                    "source": "evu_experience",
                    "model": experience.model,
                    "provider": experience.provider,
                },
            )
        )

    return output