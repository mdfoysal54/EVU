import json
from datetime import datetime

from app.research.dataset.schemas import (
    DatasetBuildResponse,
    DatasetExample,
    DatasetExportResponse,
)


class DatasetService:

    def create_version(
        self,
        examples: list[DatasetExample],
        quality_threshold: float,
        total_candidates: int,
    ) -> DatasetBuildResponse:

        version = (
            "evu-dataset-"
            + datetime.utcnow().strftime(
                "%Y%m%d-%H%M%S"
            )
        )

        return DatasetBuildResponse(
            dataset_version=version,
            total_candidates=total_candidates,
            accepted_examples=len(examples),
            rejected_examples=max(
                total_candidates - len(examples),
                0,
            ),
            quality_threshold=quality_threshold,
            examples=examples,
        )

    def export_jsonl(
        self,
        dataset: DatasetBuildResponse,
    ) -> DatasetExportResponse:

        lines = []

        for example in dataset.examples:

            record = {
                "messages": [
                    {
                        "role": "user",
                        "content": example.prompt,
                    },
                    {
                        "role": "assistant",
                        "content": example.response,
                    },
                ],

                "metadata": {
                    "request_id": example.request_id,
                    "task_type": example.task_type,
                    "provider": example.provider,
                    "model": example.model,
                    "judge_relevance": (
                        example.judge_relevance
                    ),
                    "judge_correctness": (
                        example.judge_correctness
                    ),
                    "judge_completeness": (
                        example.judge_completeness
                    ),
                    "judge_clarity": (
                        example.judge_clarity
                    ),
                    "judge_overall": (
                        example.judge_overall
                    ),
                    "user_rating": (
                        example.user_rating
                    ),
                },
            }

            lines.append(
                json.dumps(
                    record,
                    ensure_ascii=False,
                )
            )

        jsonl = "\n".join(lines)

        return DatasetExportResponse(
            dataset_version=dataset.dataset_version,
            example_count=len(dataset.examples),
            format="jsonl",
            jsonl=jsonl,
        )


dataset_service = DatasetService()