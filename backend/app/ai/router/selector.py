from __future__ import annotations

from typing import Any, Optional
from pydantic import BaseModel

from app.ai.router.capabilities import get_provider_capabilities
from app.ai.routing.advanced_selector import advanced_model_selector


class RoutingDecision(BaseModel):
    provider: str
    model: str
    score: float = 0.0
    reason: Optional[str] = None
    metadata: dict[str, Any] = {}


class EVUModelRouter:
    """Router service that manages model selection and external catalog state."""

    def __init__(self) -> None:
        self.selector = advanced_model_selector

    def update_catalog(self, provider_models: dict[str, str]) -> list[dict]:
        return build_external_model_catalog(provider_models)

    def route(self, task: str, **kwargs: Any) -> RoutingDecision:
        # Delegate routing logic to the advanced selector implementation
        if hasattr(self.selector, "select_model"):
            result = self.selector.select_model(task, **kwargs)
        elif hasattr(self.selector, "route"):
            result = self.selector.route(task, **kwargs)
        else:
            result = None

        if isinstance(result, dict):
            return RoutingDecision(**result)
        elif isinstance(result, RoutingDecision):
            return result

        return RoutingDecision(
            provider="local",
            model="gemma3",
            reason="Fallback default decision",
        )


def build_external_model_catalog(
    provider_models: dict[str, str],
) -> list[dict]:
    catalog = []

    for provider, model_name in provider_models.items():
        capabilities = get_provider_capabilities(provider)

        if not capabilities:
            continue

        catalog.append(
            {
                "provider": provider,
                "model": model_name,
                "coding": capabilities.get("coding", 0.5),
                "reasoning": capabilities.get("reasoning", 0.5),
                "research": capabilities.get("research", 0.5),
                "multimodal": capabilities.get("multimodal", 0.5),
                "writing": capabilities.get("writing", 0.5),
                "analysis": capabilities.get("analysis", 0.5),
                "general": capabilities.get("general", 0.5),
                "latency_score": capabilities.get("latency_score", 0.5),
                "cost_score": capabilities.get("cost_score", 0.5),
            }
        )

    if hasattr(advanced_model_selector, "set_external_models"):
        advanced_model_selector.set_external_models(catalog)

    return catalog


# Exported instances matching app/ai/router/__init__.py
ev_model_router = EVUModelRouter()