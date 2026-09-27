import json
import re
from collections import Counter

from app.ai.gateway import ai_gateway
from app.ai.evaluation.schemas import (
    CandidateAnswer,
    CandidateScore,
    JudgeRequest,
    JudgeResponse,
    JudgeResult,
)
from app.ai.router.selector import ev_model_router
from app.core.config import settings


class EVUEvaluationEngine:
    """Step 10 judge/reliability layer.

    This evaluates independent model answers after Step 9. It does not train
    a model and does not update model weights. The result is intended to become
    training/evaluation data for a future EVU learning pipeline.
    """

    JUDGE_SYSTEM = (
        "You are EVU's quality judge. Evaluate independent AI answers to the "
        "same user question. Score each answer from 0 to 10 for relevance, "
        "correctness, completeness, and clarity. Prefer factual accuracy, "
        "directness, useful reasoning, and appropriate caveats. Do not reward "
        "verbosity by itself. Return ONLY valid JSON with this shape: "
        '{"scores":[{"provider":"...","model":"...","relevance":0,'
        '"correctness":0,"completeness":0,"clarity":0,"overall":0,'
        '"strengths":["..."],"weaknesses":["..."]}],'
        '"winner_provider":"...","winner_model":"...",'
        '"confidence":0,"rationale":"..."}'
    )

    def _heuristic(self, request: JudgeRequest) -> JudgeResponse:
        """Offline fallback so the endpoint remains useful without a judge key."""
        question_terms = set(
            re.findall(r"[a-zA-Z0-9_]+", request.question.lower())
        )
        scores = []

        for candidate in request.candidates:
            terms = re.findall(r"[a-zA-Z0-9_]+", candidate.answer.lower())
            counts = Counter(terms)
            overlap = (
                sum(1 for term in question_terms if term in counts)
                / max(len(question_terms), 1)
            )
            relevance = min(10.0, 3.0 + overlap * 7.0)

            length = len(candidate.answer.strip())
            completeness = 4.0 if length < 120 else min(10.0, 5.0 + length / 1200)
            clarity = 7.0 if length <= 6000 else 6.0

            overall = round(
                relevance * 0.35
                + 4.5 * 0.30
                + completeness * 0.20
                + clarity * 0.15,
                2,
            )

            scores.append(
                CandidateScore(
                    provider=candidate.provider,
                    model=candidate.model,
                    relevance=round(relevance, 2),
                    correctness=4.5,
                    completeness=round(completeness, 2),
                    clarity=clarity,
                    overall=overall,
                    strengths=["Passed basic response-quality checks."],
                    weaknesses=[
                        "Offline heuristic cannot verify factual correctness."
                    ],
                )
            )

        scores.sort(key=lambda item: item.overall, reverse=True)
        winner = scores[0]

        return JudgeResponse(
            result=JudgeResult(
                winner_provider=winner.provider,
                winner_model=winner.model,
                confidence=0.35,
                rationale=(
                    "Offline heuristic evaluation was used. "
                    "It estimates relevance/completeness but cannot "
                    "reliably verify factual correctness."
                ),
                scores=scores,
            ),
            judge_provider="heuristic",
            judge_model=None,
            evaluation_mode="offline_heuristic",
        )

    def _select_judge(
        self,
        request: JudgeRequest,
    ) -> tuple[str, str | None]:
        configured = {
            item["id"]: item
            for item in ai_gateway.available_providers()
            if item["available"]
        }

        if request.judge_provider != "auto":
            if request.judge_provider not in configured:
                raise ValueError(
                    f"Judge provider '{request.judge_provider}' is not configured."
                )
            provider = request.judge_provider
        else:
            decision = ev_model_router.choose(
                "analyze and evaluate these competing answers",
                requested_provider="auto",
            )
            provider = decision.provider

        model = request.judge_model or configured[provider]["default_model"]
        return provider, model

    async def run(self, request: JudgeRequest) -> JudgeResponse:
        if not settings.EVALUATION_ENABLED:
            raise ValueError("EVU evaluation is disabled by server configuration.")

        try:
            provider, model = self._select_judge(request)
        except ValueError:
            return self._heuristic(request)

        blocks = []
        for index, candidate in enumerate(request.candidates, start=1):
            blocks.append(
                f"ANSWER {index}\n"
                f"Provider: {candidate.provider}\n"
                f"Model: {candidate.model or 'default'}\n"
                f"Answer:\n{candidate.answer[:12000]}"
            )

        prompt = (
            f"USER QUESTION:\n{request.question}\n\n"
            "CANDIDATE ANSWERS:\n\n"
            + "\n\n---\n\n".join(blocks)
        )

        try:
            raw = await ai_gateway.generate(
                [
                    {"role": "system", "content": self.JUDGE_SYSTEM},
                    {"role": "user", "content": prompt},
                ],
                provider,
                model,
            )
            payload = self._extract_json(raw)
            result = JudgeResult.model_validate(payload)

            return JudgeResponse(
                result=result,
                judge_provider=provider,
                judge_model=model,
                evaluation_mode="llm_judge",
            )
        except Exception:
            return self._heuristic(request)

    @staticmethod
    def _extract_json(raw: str) -> dict:
        text = raw.strip()
        if text.startswith("```"):
            text = re.sub(r"^```(?:json)?\s*", "", text)
            text = re.sub(r"\s*```$", "", text)

        start = text.find("{")
        end = text.rfind("}")
        if start == -1 or end == -1 or end <= start:
            raise ValueError("Judge did not return a JSON object.")

        return json.loads(text[start : end + 1])


evu_evaluation_engine = EVUEvaluationEngine()