import re

from app.ai.synthesis.schemas import SynthesisCandidate


def _tokens(text: str) -> set[str]:
    return {
        token.lower()
        for token in re.findall(r"\b[a-zA-Z0-9]{3,}\b", text)
    }


def calculate_consensus(
    candidates: list[SynthesisCandidate],
) -> float:
    """
    Estimate semantic agreement using token overlap.

    This is intentionally lightweight. A future version can
    replace this with embedding-based semantic similarity.
    """

    if len(candidates) <= 1:
        return 1.0

    token_sets = [
        _tokens(candidate.answer)
        for candidate in candidates
    ]

    scores: list[float] = []

    for index in range(len(token_sets)):
        for other in range(index + 1, len(token_sets)):
            left = token_sets[index]
            right = token_sets[other]

            if not left or not right:
                continue

            intersection = len(left & right)
            union = len(left | right)

            if union:
                scores.append(intersection / union)

    if not scores:
        return 0.0

    return round(sum(scores) / len(scores), 4)


def detect_disagreements(
    candidates: list[SynthesisCandidate],
) -> list[str]:
    """
    Detect broad disagreement signals.

    This is not a factual judge. It simply identifies cases
    where candidates appear substantially different.
    """

    if len(candidates) <= 1:
        return []

    disagreements: list[str] = []

    consensus = calculate_consensus(candidates)

    if consensus < 0.15:
        disagreements.append(
            "Candidate responses have substantial textual disagreement."
        )

    providers = {
        candidate.provider
        for candidate in candidates
    }

    if len(providers) > 1 and consensus < 0.30:
        disagreements.append(
            "Different providers produced materially different responses."
        )

    return disagreements