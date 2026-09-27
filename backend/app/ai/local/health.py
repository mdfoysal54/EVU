from typing import Any

from app.ai.local.ollama import (
    ollama_service,
)


async def get_local_model_status() -> dict[str, Any]:

    health = (
        await ollama_service.health()
    )

    models = []

    if health.get("available"):
        models = (
            await ollama_service.list_models()
        )

    return {
        "runtime": "ollama",
        "available": health.get(
            "available",
            False,
        ),
        "models": models,
    }