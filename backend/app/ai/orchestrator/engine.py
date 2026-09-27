from app.ai.gateway import ai_gateway
from app.ai.router.selector import (
    ev_model_router,
    RoutingDecision,
)
from app.ai.orchestrator.schemas import (
    OrchestrationRequest,
    OrchestrationResponse,
    RoutingInfo,
)


class EVUOrchestrator:
    """EVU's central decision layer for routing and response generation."""

    SYSTEM_PROMPT = (
        "You are EVU, a meta-orchestrator AI. Answer clearly, accurately, "
        "and honestly. You are the final response layer after EVU selected "
        "a specialized model. Never claim that another model was consulted "
        "unless the orchestration metadata says so."
    )

    def route(
        self,
        request: OrchestrationRequest,
    ) -> RoutingDecision:
        return ev_model_router.choose(
            request.message,
            requested_provider=request.provider,
            requested_model=request.model,
        )

    async def run(
        self,
        request: OrchestrationRequest,
    ) -> OrchestrationResponse:
        decision = self.route(request)

        messages = [
            {
                "role": "system",
                "content": self.SYSTEM_PROMPT,
            },
            {
                "role": "user",
                "content": request.message,
            },
        ]

        answer = await ai_gateway.generate(
            messages,
            decision.provider,
            decision.model,
        )

        return OrchestrationResponse(
            response=answer,
            provider=decision.provider,
            model=decision.model,
            task=decision.task,
            routing=RoutingInfo(
                provider=decision.provider,
                model=decision.model,
                task=decision.task,
                confidence=decision.confidence,
                reason=decision.reason,
                candidates=decision.candidates,
            ),
        )


evu_orchestrator = EVUOrchestrator()