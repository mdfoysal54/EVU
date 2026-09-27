from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from app.ai.local.registry import (
    LocalModel,
    local_model_registry,
)
from app.ai.routing.policy import (
    RoutingPolicy,
)


@dataclass
class ModelCandidate:

    provider: str

    model: str

    score: float

    reason: str

    local: bool

    capabilities: dict[str, float]


class AdvancedModelSelector:

    TASK_CAPABILITY_MAP = {
        "coding": "coding",
        "research": "research",
        "multimodal": "analysis",
        "writing": "writing",
        "analysis": "analysis",
        "reasoning": "reasoning",
        "general": "general",
    }

    def __init__(self) -> None:

        self.external_models: list[
            dict[str, Any]
        ] = []

    def set_external_models(
        self,
        models: list[dict[str, Any]],
    ) -> None:

        self.external_models = models

    def _score_local(
        self,
        model: LocalModel,
        task_type: str,
        policy: RoutingPolicy,
    ) -> float:

        capability_name = (
            self.TASK_CAPABILITY_MAP.get(
                task_type,
                "general",
            )
        )

        capability = getattr(
            model,
            capability_name,
            model.general,
        )

        score = (
            capability
            * policy.quality_priority
        )

        if policy.prefer_local:
            score += 0.15

        if policy.privacy_sensitive:
            score += (
                model.privacy
                * policy.privacy_priority
            )

        if policy.latency_sensitive:
            score += (
                model.latency_score
                * policy.latency_priority
            )

        if (
            policy.cost_priority > 0
            and model.cost_per_1m_input == 0
        ):
            score += (
                policy.cost_priority
            )

        return min(
            max(score, 0.0),
            1.0,
        )

    def _score_external(
        self,
        model: dict[str, Any],
        task_type: str,
        policy: RoutingPolicy,
    ) -> float:

        capability_name = (
            self.TASK_CAPABILITY_MAP.get(
                task_type,
                "general",
            )
        )

        capability = float(
            model.get(
                capability_name,
                model.get(
                    "general",
                    0.5,
                ),
            )
        )

        score = (
            capability
            * policy.quality_priority
        )

        provider = model.get(
            "provider"
        )

        if policy.prefer_local:
            score -= 0.15

        if policy.privacy_sensitive:
            score -= (
                policy.privacy_priority
                * 0.20
            )

        latency = float(
            model.get(
                "latency_score",
                0.6,
            )
        )

        if policy.latency_sensitive:
            score += (
                latency
                * policy.latency_priority
            )

        cost = float(
            model.get(
                "cost_score",
                0.5,
            )
        )

        score += (
            cost
            * policy.cost_priority
        )

        return min(
            max(score, 0.0),
            1.0,
        )

    async def rank(
        self,
        task_type: str,
        policy: RoutingPolicy | None = None,
    ) -> list[ModelCandidate]:

        policy = (
            policy
            or RoutingPolicy()
        )

        candidates: list[
            ModelCandidate
        ] = []

        # ---------------------------------------------
        # LOCAL MODELS
        # ---------------------------------------------

        if policy.allow_local:

            await local_model_registry.refresh()

            for model in (
                local_model_registry.get_all()
            ):

                if not model.enabled:
                    continue

                score = self._score_local(
                    model=model,
                    task_type=task_type,
                    policy=policy,
                )

                if (
                    score
                    < policy.minimum_quality
                ):
                    continue

                candidates.append(
                    ModelCandidate(
                        provider=model.provider,
                        model=model.model,
                        score=score,
                        reason=(
                            "Local model selected "
                            "using task capability "
                            "and routing policy."
                        ),
                        local=True,
                        capabilities={
                            "coding": model.coding,
                            "reasoning": model.reasoning,
                            "research": model.research,
                            "writing": model.writing,
                            "analysis": model.analysis,
                            "general": model.general,
                        },
                    )
                )

        # ---------------------------------------------
        # EXTERNAL MODELS
        # ---------------------------------------------

        if policy.allow_external:

            for model in (
                self.external_models
            ):

                provider = model.get(
                    "provider"
                )

                model_name = model.get(
                    "model"
                )

                if not provider or not model_name:
                    continue

                if (
                    policy.explicit_provider
                    and provider
                    != policy.explicit_provider
                ):
                    continue

                if (
                    policy.explicit_model
                    and model_name
                    != policy.explicit_model
                ):
                    continue

                score = self._score_external(
                    model=model,
                    task_type=task_type,
                    policy=policy,
                )

                if (
                    score
                    < policy.minimum_quality
                ):
                    continue

                candidates.append(
                    ModelCandidate(
                        provider=provider,
                        model=model_name,
                        score=score,
                        reason=(
                            "External model selected "
                            "using task capability "
                            "and routing policy."
                        ),
                        local=False,
                        capabilities={
                            "coding": float(
                                model.get(
                                    "coding",
                                    0.5,
                                )
                            ),
                            "reasoning": float(
                                model.get(
                                    "reasoning",
                                    0.5,
                                )
                            ),
                            "research": float(
                                model.get(
                                    "research",
                                    0.5,
                                )
                            ),
                            "writing": float(
                                model.get(
                                    "writing",
                                    0.5,
                                )
                            ),
                            "analysis": float(
                                model.get(
                                    "analysis",
                                    0.5,
                                )
                            ),
                            "general": float(
                                model.get(
                                    "general",
                                    0.5,
                                )
                            ),
                        },
                    )
                )

        candidates.sort(
            key=lambda item: item.score,
            reverse=True,
        )

        return candidates

    async def select(
        self,
        task_type: str,
        policy: RoutingPolicy | None = None,
    ) -> ModelCandidate | None:

        candidates = await self.rank(
            task_type=task_type,
            policy=policy,
        )

        if not candidates:
            return None

        return candidates[0]


advanced_model_selector = (
    AdvancedModelSelector()
)