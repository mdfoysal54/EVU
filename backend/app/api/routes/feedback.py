from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
)
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user
from app.core.config import settings
from app.database.database import get_db
from app.database.models import User
from app.feedback.schemas import (
    FeedbackCreate,
    FeedbackResponse,
)
from app.feedback.service import feedback_service


router = APIRouter(
    prefix="/api/v1/feedback",
    tags=["EVU Feedback"],
)


@router.post(
    "",
    response_model=FeedbackResponse,
)
def create_feedback(
    payload: FeedbackCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if not settings.FEEDBACK_ENABLED:
        raise HTTPException(
            status_code=503,
            detail="EVU feedback is disabled.",
        )

    try:
        return feedback_service.create(
            db=db,
            user_id=current_user.id,
            payload=payload,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc