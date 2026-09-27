from app.ai.synthesis.schemas import SynthesisCandidate


def normalize_candidates(
    candidates: list[SynthesisCandidate],
) -> list[SynthesisCandidate]:
    """
    Normalize and rank synthesis candidates.
    """

    normalized: list[SynthesisCandidate] = []

    for candidate in candidates:
        answer = candidate.answer.strip()

        if not answer:
            continue

        score = max(0.0, min(1.0, candidate.score))
        confidence = max(0.0, min(1.0, candidate.confidence))

        normalized.append(
            candidate.model_copy(
                update={
                    "answer": answer,
                    "score": score,
                    "confidence": confidence,
                }
            )
        )

    normalized.sort(
        key=lambda item: (
            item.score * 0.6
            + item.confidence * 0.4
        ),
        reverse=True,
    )

    return normalized