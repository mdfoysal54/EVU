from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from app.ai.local.ollama import ollama_service


@dataclass
class LocalModel:
    provider: str
    model: str

    display_name: str

    coding: float
    reasoning: float
    research: float
    writing: float
    analysis: float
    general: float

    context_window: int

    vision: bool = False
    tools: bool = False

    privacy: float = 1.0

    cost_per_1m_input: float = 0.0
    cost_per_1m_output: float = 0.0

    latency_score: float = 0.6

    enabled: bool = True


class LocalModelRegistry:

    def __init__(self) -> None:

        self._models: dict[
            str,
            LocalModel,
        ] = {}

    def register(
        self,
        model: LocalModel,
    ) -> None:

        key = (
            f"{model.provider}:"
            f"{model.model}"
        )

        self._models[key] = model

    def get_all(
        self,
    ) -> list[LocalModel]:

        return list(
            self._models.values()
        )

    def get(
        self,
        provider: str,
        model_name: str,
    ) -> LocalModel | None:

        return self._models.get(
            f"{provider}:{model_name}"
        )

    def remove(
        self,
        provider: str,
        model_name: str,
    ) -> None:

        self._models.pop(
            f"{provider}:{model_name}",
            None,
        )

    async def discover_ollama(
        self,
    ) -> list[LocalModel]:

        discovered: list[
            LocalModel
        ] = []

        models = (
            await ollama_service.list_models()
        )

        for item in models:

            name = item.get(
                "name"
            )

            if not name:
                continue

            model = LocalModel(
                provider="ollama",
                model=name,
                display_name=name,
                coding=0.70,
                reasoning=0.65,
                research=0.55,
                writing=0.70,
                analysis=0.65,
                general=0.75,
                context_window=8192,
                vision=(
                    "vision"
                    in name.lower()
                    or "gemma3"
                    in name.lower()
                ),
                tools=False,
                privacy=1.0,
                latency_score=0.65,
                enabled=True,
            )

            self.register(model)

            discovered.append(model)

        return discovered

    async def refresh(
        self,
    ) -> list[LocalModel]:

        return await self.discover_ollama()

    def as_dict(
        self,
    ) -> list[dict[str, Any]]:

        return [
            {
                "provider": model.provider,
                "model": model.model,
                "display_name": model.display_name,
                "coding": model.coding,
                "reasoning": model.reasoning,
                "research": model.research,
                "writing": model.writing,
                "analysis": model.analysis,
                "general": model.general,
                "context_window": model.context_window,
                "vision": model.vision,
                "tools": model.tools,
                "privacy": model.privacy,
                "latency_score": model.latency_score,
                "enabled": model.enabled,
            }
            for model in self.get_all()
        ]


local_model_registry = LocalModelRegistry()