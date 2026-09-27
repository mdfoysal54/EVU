from collections import defaultdict
from datetime import datetime, timedelta, timezone

from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.telemetry.models import TelemetryEvent
from app.telemetry.schemas import (
    ModelPerformance,
    ModelPerformanceResponse,
    TelemetryEventCreate,
    TelemetryEventResponse,
)


class TelemetryService:
    def record(
        self,
        db: Session,
        user_id: int | None,
        event: TelemetryEventCreate,
    ) -> TelemetryEventResponse:
        row = TelemetryEvent(
            request_id=event.request_id,
            user_id=user_id,
            event_type=event.event_type,
            task_type=event.task_type,
            provider=event.provider,
            model=event.model,
            success=event.success,
            latency_ms=event.latency_ms,
            input_tokens=event.input_tokens,
            output_tokens=event.output_tokens,
            total_tokens=event.total_tokens,
            estimated_cost=event.estimated_cost,
            error_type=event.error_type,
            error_message=event.error_message,
            judge_relevance=event.judge_relevance,
            judge_correctness=event.judge_correctness,
            judge_completeness=event.judge_completeness,
            judge_clarity=event.judge_clarity,
            judge_overall=event.judge_overall,
            judge_winner=event.judge_winner,
            metadata_json=event.metadata,
        )

        db.add(row)
        db.commit()
        db.refresh(row)

        return TelemetryEventResponse.model_validate(row)

    def performance(
        self,
        db: Session,
        user_id: int | None,
        window_days: int,
    ) -> ModelPerformanceResponse:
        since = (
            datetime.now(timezone.utc)
            - timedelta(days=window_days)
        )

        query = select(TelemetryEvent).where(
            TelemetryEvent.created_at >= since
        )

        if user_id is not None:
            query = query.where(
                TelemetryEvent.user_id == user_id
            )

        rows = db.scalars(query).all()

        buckets = defaultdict(list)

        for row in rows:
            key = (
                row.provider,
                row.model,
                row.task_type,
            )

            buckets[key].append(row)

        output: list[ModelPerformance] = []

        for (
            provider,
            model,
            task_type,
        ), items in buckets.items():

            count = len(items)

            successful = sum(
                1
                for item in items
                if item.success
            )

            failed = count - successful

            latencies = [
                item.latency_ms
                for item in items
                if item.latency_ms is not None
            ]

            scores = [
                item.judge_overall
                for item in items
                if item.judge_overall is not None
            ]

            relevance = [
                item.judge_relevance
                for item in items
                if item.judge_relevance is not None
            ]

            correctness = [
                item.judge_correctness
                for item in items
                if item.judge_correctness is not None
            ]

            completeness = [
                item.judge_completeness
                for item in items
                if item.judge_completeness is not None
            ]

            clarity = [
                item.judge_clarity
                for item in items
                if item.judge_clarity is not None
            ]

            winners = sum(
                1
                for item in items
                if item.judge_winner is True
            )

            total_input_tokens = sum(
                item.input_tokens or 0
                for item in items
            )

            total_output_tokens = sum(
                item.output_tokens or 0
                for item in items
            )

            total_tokens = sum(
                item.total_tokens or 0
                for item in items
            )

            estimated_cost = sum(
                item.estimated_cost or 0.0
                for item in items
            )

            output.append(
                ModelPerformance(
                    provider=provider,
                    model=model,
                    task_type=task_type,
                    request_count=count,
                    successful_requests=successful,
                    failed_requests=failed,
                    success_rate=round(
                        successful / count,
                        4,
                    )
                    if count
                    else 0.0,
                    average_latency_ms=round(
                        sum(latencies) / len(latencies),
                        2,
                    )
                    if latencies
                    else None,
                    average_score=round(
                        sum(scores) / len(scores),
                        3,
                    )
                    if scores
                    else None,
                    average_relevance=round(
                        sum(relevance) / len(relevance),
                        3,
                    )
                    if relevance
                    else None,
                    average_correctness=round(
                        sum(correctness) / len(correctness),
                        3,
                    )
                    if correctness
                    else None,
                    average_completeness=round(
                        sum(completeness) / len(completeness),
                        3,
                    )
                    if completeness
                    else None,
                    average_clarity=round(
                        sum(clarity) / len(clarity),
                        3,
                    )
                    if clarity
                    else None,
                    winner_count=winners,
                    winner_rate=round(
                        winners / count,
                        4,
                    )
                    if count
                    else None,
                    total_input_tokens=total_input_tokens,
                    total_output_tokens=total_output_tokens,
                    total_tokens=total_tokens,
                    estimated_cost=round(
                        estimated_cost,
                        8,
                    ),
                )
            )

        output.sort(
            key=lambda item: (
                item.average_score
                if item.average_score is not None
                else -1,
                item.success_rate,
                item.winner_rate
                if item.winner_rate is not None
                else -1,
                -(
                    item.average_latency_ms
                    if item.average_latency_ms is not None
                    else 10**12
                ),
            ),
            reverse=True,
        )

        return ModelPerformanceResponse(
            window_days=window_days,
            generated_at=datetime.now(timezone.utc),
            models=output,
        )

    def cleanup(
        self,
        db: Session,
        user_id: int | None,
    ) -> int:
        retention_days = settings.TELEMETRY_RETENTION_DAYS

        cutoff = (
            datetime.now(timezone.utc)
            - timedelta(days=retention_days)
        )

        query = delete(TelemetryEvent).where(
            TelemetryEvent.created_at < cutoff
        )

        if user_id is not None:
            query = query.where(
                TelemetryEvent.user_id == user_id
            )

        result = db.execute(query)
        db.commit()

        return result.rowcount or 0


telemetry_service = TelemetryService()