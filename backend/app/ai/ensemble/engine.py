import asyncio

from app.ai.gateway import ai_gateway
from app.ai.router.selector import ev_model_router
from app.ai.ensemble.schemas import (
    EnsembleRequest,
    EnsembleResponse,
    ModelAnswer,
)
from app.core.config import settings


class EVUEnsemble:
    """Step 9 multi-model ensemble and synthesis layer.

    Step 8 selects one best provider. Step 9 can consult several configured
    providers in parallel, then optionally ask a synthesis model to reconcile
    the independent answers into one EVU response.
    """

    SYNTHESIS_SYSTEM = (
        "You are EVU's synthesis layer. You receive independent answers from "
        "multiple AI models. Produce one accurate, useful final answer. "
        "Resolve contradictions using reasoning, preserve important caveats, "
        "and do not mention provider names unless the user asks. Do not invent "
        "facts that are absent from the supplied answers."
    )

    async def _call_provider(
        self,
        message: str,
        provider: str,
        model: str | None,
    ) -> ModelAnswer:
        try:
            answer = await asyncio.wait_for(
                ai_gateway.generate(
                    [
                        {
                            "role": "system",
                            "content": "Answer the user's request independently and clearly.",
                        },
                        {"role": "user", "content": message},
                    ],
                    provider,
                    model,
                ),
                timeout=settings.ENSEMBLE_TIMEOUT_SECONDS,
            )
            return ModelAnswer(
                provider=provider,
                model=model,
                answer=answer,
            )
        except Exception as exc:
            return ModelAnswer(
                provider=provider,
                model=model,
                answer="",
                success=False,
                error=str(exc),
            )

    def _candidate_providers(
        self,
        request: EnsembleRequest,
    ) -> tuple[str, float, list[dict]]:
        decision = ev_model_router.choose(
            request.message,
            requested_provider=request.provider,
            requested_model=request.model,
        )

        limit = request.max_models or settings.ENSEMBLE_MAX_MODELS
        candidates = decision.candidates[:limit]

        return decision.task, decision.confidence, candidates

    async def _synthesize(
        self,
        original_message: str,
        answers: list[ModelAnswer],
        provider: str,
        model: str | None,
    ) -> str:
        blocks = []
        for index, item in enumerate(answers, start=1):
            blocks.append(
                f"MODEL ANSWER {index}\n"
                f"Provider: {item.provider}\n"
                f"Answer:\n{item.answer[:8000]}"
            )

        prompt = (
            f"Original user request:\n{original_message}\n\n"
            "Independent model answers:\n\n"
            + "\n\n---\n\n".join(blocks)
            + "\n\nNow synthesize the best final answer."
        )

        return await asyncio.wait_for(
            ai_gateway.generate(
                [
                    {"role": "system", "content": self.SYNTHESIS_SYSTEM},
                    {"role": "user", "content": prompt},
                ],
                provider,
                model,
            ),
            timeout=settings.ENSEMBLE_TIMEOUT_SECONDS,
        )

    async def run(self, request: EnsembleRequest) -> EnsembleResponse:
        if not settings.ENSEMBLE_ENABLED:
            raise ValueError(
                "Multi-model ensemble is disabled by server configuration."
            )

        task, confidence, candidates = self._candidate_providers(request)

        if not candidates:
            raise ValueError("No configured AI providers are available for ensemble mode.")

        selected = []
        for item in candidates:
            provider = item["provider"]
            model = request.model if request.provider != "auto" else None
            if model is None:
                model = next(
                    p["default_model"]
                    for p in ai_gateway.available_providers()
                    if p["id"] == provider
                )
            selected.append((provider, model))

        results = await asyncio.gather(
            *[
                self._call_provider(request.message, provider, model)
                for provider, model in selected
            ]
        )

        successful = [item for item in results if item.success and item.answer.strip()]
        if not successful:
            errors = "; ".join(
                f"{item.provider}: {item.error or 'unknown error'}"
                for item in results
            )
            raise ValueError(f"All ensemble providers failed. {errors}")

        if not request.synthesize or len(successful) == 1:
            return EnsembleResponse(
                response=successful[0].answer,
                task=task,
                confidence=confidence,
                models_consulted=results,
            )

        synthesis_provider = settings.ENSEMBLE_SYNTHESIS_PROVIDER
        configured = {
            item["id"]
            for item in ai_gateway.available_providers()
            if item["available"]
        }

        if synthesis_provider not in configured:
            synthesis_provider = successful[0].provider

        synthesis_model = next(
            item["default_model"]
            for item in ai_gateway.available_providers()
            if item["id"] == synthesis_provider
        )

        try:
            final_answer = await self._synthesize(
                request.message,
                successful,
                synthesis_provider,
                synthesis_model,
            )
        except Exception:
            # If synthesis fails, preserve a successful model answer rather than
            # turning a partially successful ensemble into a total failure.
            final_answer = successful[0].answer
            synthesis_provider = successful[0].provider
            synthesis_model = successful[0].model

        return EnsembleResponse(
            response=final_answer,
            task=task,
            confidence=confidence,
            synthesis_provider=synthesis_provider,
            synthesis_model=synthesis_model,
            models_consulted=results,
        )


evu_ensemble = EVUEnsemble()