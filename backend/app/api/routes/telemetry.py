from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
)
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user
from app.core.config import settings
from app.database.database import get_db
from app.database.models import User
from app.telemetry.schemas import (
    ModelPerformanceResponse,
    TelemetryEventCreate,
    TelemetryEventResponse,
)
from app.telemetry.service import telemetry_service


router = APIRouter(
    prefix="/api/v1/telemetry",
    tags=["EVU Telemetry"],
)


@router.post(
    "/events",
    response_model=TelemetryEventResponse,
)
def create_telemetry_event(
    payload: TelemetryEventCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if not settings.TELEMETRY_ENABLED:
        raise HTTPException(
            status_code=503,
            detail="EVU telemetry is disabled.",
        )

    return telemetry_service.record(
        db=db,
        user_id=current_user.id,
        event=payload,
    )


@router.get(
    "/model-performance",
    response_model=ModelPerformanceResponse,
)
def model_performance(
    window_days: int = Query(
        default=30,
        ge=1,
        le=3650,
    ),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if not settings.TELEMETRY_ENABLED:
        raise HTTPException(
            status_code=503,
            detail="EVU telemetry is disabled.",
        )

    return telemetry_service.performance(
        db=db,
        user_id=current_user.id,
        window_days=window_days,
    )


@router.post("/cleanup")
def cleanup_telemetry(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if not settings.TELEMETRY_ENABLED:
        raise HTTPException(
            status_code=503,
            detail="EVU telemetry is disabled.",
        )

    deleted = telemetry_service.cleanup(
        db=db,
        user_id=current_user.id,
    )

    return {
        "status": "success",
        "deleted_events": deleted,
        "retention_days": settings.TELEMETRY_RETENTION_DAYS,
    }