from datetime import datetime

from sqlalchemy import and_, or_
from sqlalchemy.orm import Session

from app.database.models import Conversation, Message
from app.telemetry.models import (
    TelemetryEvent,
    UserFeedback,
)

from app.research.dataset.schemas import (
    DatasetBuildRequest,
    DatasetExample,
)


class DatasetBuilder:
    """
    Converts high-quality EVU interactions into supervised training examples.

    The builder intentionally uses existing EVU data rather than introducing
    another database table at this stage.
    """

    def build(
        self,
        db: Session,
        user_id: int,
        request: DatasetBuildRequest,
    ) -> tuple[list[DatasetExample], int]:

        telemetry_rows = (
            db.query(TelemetryEvent)
            .filter(
                TelemetryEvent.user_id == user_id,
                TelemetryEvent.success.is_(True),
            )
            .order_by(TelemetryEvent.created_at.desc())
            .limit(request.max_examples * 5)
            .all()
        )

        examples: list[DatasetExample] = []

        for telemetry in telemetry_rows:
            if (
                request.require_judge_score
                and telemetry.judge_overall is None
            ):
                continue

            if (
                telemetry.judge_overall is not None
                and telemetry.judge_overall < request.min_judge_score
            ):
                continue

            feedback = (
                db.query(UserFeedback)
                .filter(
                    UserFeedback.user_id == user_id,
                    UserFeedback.request_id == telemetry.request_id,
                )
                .order_by(UserFeedback.created_at.desc())
                .first()
            )

            if request.require_user_feedback and feedback is None:
                continue

            if (
                feedback is not None
                and feedback.rating < request.min_user_rating
            ):
                continue

            prompt, response = self._find_conversation_content(
                db,
                user_id,
                telemetry.request_id,
            )

            if not prompt or not response:
                continue

            examples.append(
                DatasetExample(
                    request_id=telemetry.request_id,
                    task_type=telemetry.task_type,
                    prompt=prompt,
                    response=response,
                    provider=telemetry.provider,
                    model=telemetry.model,
                    judge_relevance=telemetry.judge_relevance,
                    judge_correctness=telemetry.judge_correctness,
                    judge_completeness=telemetry.judge_completeness,
                    judge_clarity=telemetry.judge_clarity,
                    judge_overall=telemetry.judge_overall,
                    user_rating=feedback.rating if feedback else None,
                    user_comment=feedback.comment if feedback else None,
                    created_at=telemetry.created_at,
                )
            )

            if len(examples) >= request.max_examples:
                break

        return examples, len(telemetry_rows)

    def _find_conversation_content(
        self,
        db: Session,
        user_id: int,
        request_id: str,
    ) -> tuple[str | None, str | None]:
        """
        Try to find a matching conversation.

        Telemetry does not explicitly store conversation_id directly,
        so this method searches for request_id markers in message history.
        If no exact relationship exists, it returns None.
        """
        conversations = (
            db.query(Conversation)
            .filter(Conversation.user_id == user_id)
            .order_by(Conversation.created_at.desc())
            .limit(50)
            .all()
        )

        for conversation in conversations:
            messages = (
                db.query(Message)
                .filter(Message.conversation_id == conversation.id)
                .order_by(Message.created_at.asc())
                .all()
            )

            if not messages:
                continue

            for index, message in enumerate(messages):
                if (
                    message.role == "user"
                    and request_id in message.content
                ):
                    for next_message in messages[index + 1 :]:
                        if next_message.role == "assistant":
                            return (
                                message.content,
                                next_message.content,
                            )

        return None, None


dataset_builder = DatasetBuilder()