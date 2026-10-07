from __future__ import annotations

from dataclasses import dataclass, asdict
from datetime import datetime, timezone
import json
from pathlib import Path


@dataclass
class ModelManifest:
    model_id: str
    version: str
    artifact_path: str
    checksum: str
    dataset_version: str
    benchmark_score: float
    safety_score: float
    created_at: str
    metadata: dict

    @classmethod
    def create(
        cls,
        *,
        model_id: str,
        version: str,
        artifact_path: str,
        checksum: str,
        dataset_version: str,
        benchmark_score: float,
        safety_score: float,
        metadata: dict | None = None,
    ) -> "ModelManifest":
        return cls(
            model_id=model_id,
            version=version,
            artifact_path=artifact_path,
            checksum=checksum,
            dataset_version=dataset_version,
            benchmark_score=benchmark_score,
            safety_score=safety_score,
            created_at=(
                datetime.now(
                    timezone.utc
                ).isoformat()
            ),
            metadata=metadata or {},
        )

    def save(
        self,
        path: str | Path,
    ) -> None:
        path = Path(path)

        path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        path.write_text(
            json.dumps(
                asdict(self),
                indent=2,
            ),
            encoding="utf-8",
        )