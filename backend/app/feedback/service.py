from sqlalchemy import select
from sqlalchemy.orm import Session

from app.feedback.schemas import (
    FeedbackCreate,
    FeedbackResponse,
)
from app.telemetry.models import (
    TelemetryEvent,
    UserFeedback,
)


class FeedbackService:
    def create(
        self,
        db: Session,
        user_id: int,
        payload: FeedbackCreate,
    ) -> FeedbackResponse:

        telemetry_query = (
            select(TelemetryEvent.id)
            .where(
                TelemetryEvent.request_id
                == payload.request_id
            )
            .where(
                TelemetryEvent.user_id == user_id
            )
            .limit(1)
        )

        telemetry_exists = db.scalar(
            telemetry_query
        )

        if telemetry_exists is None:
            raise ValueError(
                "The request_id does not belong to "
                "an EVU request for this user."
            )

        row = UserFeedback(
            request_id=payload.request_id,
            user_id=user_id,
            rating=payload.rating,
            helpful=payload.helpful,
            feedback_type=payload.feedback_type,
            comment=payload.comment,
        )

        db.add(row)
        db.commit()
        db.refresh(row)

        return FeedbackResponse.model_validate(row)


feedback_service = FeedbackService()