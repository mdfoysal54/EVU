from __future__ import annotations

from dataclasses import dataclass, field

from .schema import (
    ExperienceEvaluation,
    ExperienceRecord,
)


@dataclass
class EvaluationResult:
    evaluation: ExperienceEvaluation

    accepted: bool

    reasons: list[str] = field(
        default_factory=list
    )


class ExperienceEvaluator:
    """
    Baseline evaluator for EVU experiences.

    Scores are normalized to [0, 1].
    """

    def __init__(
        self,
        minimum_overall: float = 0.70,
    ) -> None:

        if not 0.0 <= minimum_overall <= 1.0:
            raise ValueError(
                "minimum_overall must be between 0 and 1"
            )

        self.minimum_overall = minimum_overall

    def evaluate(
        self,
        experience: ExperienceRecord,
    ) -> EvaluationResult:

        reasons: list[str] = []

        correctness = self._correctness(
            experience,
            reasons,
        )

        usefulness = self._usefulness(
            experience,
            reasons,
        )

        safety = self._safety(
            experience,
            reasons,
        )

        tool_success = self._tool_success(
            experience,
            reasons,
        )

        overall = (
            correctness * 0.35
            + usefulness * 0.30
            + safety * 0.20
            + tool_success * 0.15
        )

        passed = (
            experience.success
            and overall >= self.minimum_overall
            and safety >= 0.70
        )

        evaluation = ExperienceEvaluation(
            correctness=correctness,
            usefulness=usefulness,
            safety=safety,
            tool_success=tool_success,
            overall=overall,
            passed=passed,
            evaluator="heuristic_v1",
            reasons=reasons,
        )

        return EvaluationResult(
            evaluation=evaluation,
            accepted=passed,
            reasons=reasons,
        )

    def _correctness(
        self,
        experience: ExperienceRecord,
        reasons: list[str],
    ) -> float:

        if not experience.success:
            reasons.append(
                "Experience execution was unsuccessful."
            )
            return 0.0

        if not experience.response.strip():
            reasons.append(
                "Response is empty."
            )
            return 0.0

        score = 0.75

        if experience.error:
            score -= 0.40

        if any(
            not step.success
            for step in experience.steps
        ):
            score -= 0.20

        if score >= 0.75:
            reasons.append(
                "Execution completed with a non-empty response."
            )

        return max(
            0.0,
            min(1.0, score),
        )

    def _usefulness(
        self,
        experience: ExperienceRecord,
        reasons: list[str],
    ) -> float:

        prompt = experience.prompt.strip()
        response = experience.response.strip()

        if not prompt or not response:
            return 0.0

        score = 0.70

        if len(response) >= 20:
            score += 0.10

        if len(response) > 12000:
            score -= 0.10

        if response.lower().startswith(
            ("i don't know", "i cannot")
        ):
            score -= 0.15

        if score >= 0.70:
            reasons.append(
                "Response contains usable content."
            )

        return max(
            0.0,
            min(1.0, score),
        )

    def _safety(
        self,
        experience: ExperienceRecord,
        reasons: list[str],
    ) -> float:

        # Block 5 does not attempt to implement
        # a full safety classifier.
        #
        # It instead respects explicit failure metadata
        # and leaves room for the future safety subsystem.

        metadata = experience.metadata

        if metadata.get("safety_failed") is True:
            reasons.append(
                "Experience was explicitly marked as safety-failed."
            )
            return 0.0

        if metadata.get("safety_score") is not None:
            try:
                score = float(
                    metadata["safety_score"]
                )

                return max(
                    0.0,
                    min(1.0, score),
                )

            except (
                TypeError,
                ValueError,
            ):
                pass

        return 1.0

    def _tool_success(
        self,
        experience: ExperienceRecord,
        reasons: list[str],
    ) -> float:

        calls = experience.tool_calls

        for step in experience.steps:
            calls.extend(step.tool_calls)

        if not calls:
            return 1.0

        successful = sum(
            1
            for call in calls
            if call.success
        )

        score = successful / len(calls)

        if score < 1.0:
            reasons.append(
                "At least one tool call failed."
            )

        return score