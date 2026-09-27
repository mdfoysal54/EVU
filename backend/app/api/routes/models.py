from fastapi import APIRouter, Depends

from app.ai.local.health import (
    get_local_model_status,
)
from app.ai.local.registry import (
    local_model_registry,
)
from app.ai.routing.advanced_selector import (
    advanced_model_selector,
)
from app.ai.routing.policy import (
    RoutingPolicy,
)
from app.auth.dependencies import (
    get_current_user,
)


router = APIRouter(
    prefix="/api/v1/models",
    tags=["EVU Model Intelligence"],
)


@router.get(
    "/local",
)
async def local_models(
    current_user=Depends(
        get_current_user
    ),
):

    status = (
        await get_local_model_status()
    )

    await local_model_registry.refresh()

    return {
        "runtime": status.get(
            "runtime"
        ),
        "available": status.get(
            "available"
        ),
        "models": (
            local_model_registry.as_dict()
        ),
    }


@router.post(
    "/local/refresh",
)
async def refresh_local_models(
    current_user=Depends(
        get_current_user
    ),
):

    models = (
        await local_model_registry.refresh()
    )

    return {
        "count": len(models),
        "models": (
            local_model_registry.as_dict()
        ),
    }


@router.post(
    "/route",
)
async def route_model(
    task_type: str,
    prefer_local: bool = False,
    privacy_sensitive: bool = False,
    latency_sensitive: bool = False,
    current_user=Depends(
        get_current_user
    ),
):

    policy = RoutingPolicy(
        prefer_local=prefer_local,
        privacy_sensitive=privacy_sensitive,
        latency_sensitive=latency_sensitive,
    )

    selected = (
        await advanced_model_selector.select(
            task_type=task_type,
            policy=policy,
        )
    )

    if selected is None:

        return {
            "selected": None,
            "candidates": [],
        }

    candidates = (
        await advanced_model_selector.rank(
            task_type=task_type,
            policy=policy,
        )
    )

    return {
        "selected": {
            "provider": selected.provider,
            "model": selected.model,
            "score": selected.score,
            "local": selected.local,
            "reason": selected.reason,
        },

        "candidates": [
            {
                "provider": item.provider,
                "model": item.model,
                "score": item.score,
                "local": item.local,
                "reason": item.reason,
            }
            for item in candidates
        ],
    }