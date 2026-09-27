from fastapi import APIRouter, Depends

from app.api.dependencies import get_current_user
from app.observability.service import (
    observability_service,
)
from app.security.service import (
    security_service,
)

router = APIRouter(
    prefix="/api/v1/observability",
    tags=["EVU Observability"],
)


def _is_admin(user) -> bool:
    role = security_service.resolve_role(user)
    return role.value == "admin"


@router.get("/metrics")
async def metrics(
    current_user=Depends(get_current_user),
):
    if not _is_admin(current_user):
        return {
            "error": "Admin permission required."
        }

    return {
        "metrics": observability_service.snapshot()
    }


@router.get("/health")
async def observability_health(
    current_user=Depends(get_current_user),
):
    metrics = observability_service.snapshot()

    total_requests = sum(
        item.get("count", 0)
        for item in metrics.values()
    )

    total_failures = sum(
        item.get("failure_count", 0)
        for item in metrics.values()
    )

    return {
        "status": "ok",
        "metrics_available": True,
        "metric_count": len(metrics),
        "total_observations": total_requests,
        "total_failures": total_failures,
    }