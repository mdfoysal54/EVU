from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, Optional
import uuid


@dataclass
class ModelVersion:
    model_id: str
    version: str
    version_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    artifact_path: Optional[str] = None
    checksum: Optional[str] = None
    metrics: Dict[str, float] = field(default_factory=dict)
    config: Dict[str, Any] = field(default_factory=dict)
    notes: str = ""
    created_at: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )


class VersionRegistry:
    def __init__(self) -> None:
        self._versions: Dict[str, list[ModelVersion]] = {}

    def register(self, version: ModelVersion) -> ModelVersion:
        versions = self._versions.setdefault(
            version.model_id,
            [],
        )

        existing = next(
            (
                item
                for item in versions
                if item.version == version.version
            ),
            None,
        )

        if existing is not None:
            raise ValueError(
                f"Version already exists: "
                f"{version.model_id}:{version.version}"
            )

        versions.append(version)

        versions.sort(
            key=lambda item: item.created_at,
            reverse=True,
        )

        return version

    def create(
        self,
        model_id: str,
        version: str,
        artifact_path: Optional[str] = None,
        metrics: Optional[Dict[str, float]] = None,
        config: Optional[Dict[str, Any]] = None,
        notes: str = "",
    ) -> ModelVersion:
        return self.register(
            ModelVersion(
                model_id=model_id,
                version=version,
                artifact_path=artifact_path,
                metrics=metrics or {},
                config=config or {},
                notes=notes,
            )
        )

    def get(
        self,
        model_id: str,
        version: str,
    ) -> Optional[ModelVersion]:
        for item in self._versions.get(model_id, []):
            if item.version == version:
                return item

        return None

    def latest(
        self,
        model_id: str,
    ) -> Optional[ModelVersion]:
        versions = self._versions.get(model_id, [])

        if not versions:
            return None

        return versions[0]

    def list(
        self,
        model_id: str,
    ) -> list[ModelVersion]:
        return list(self._versions.get(model_id, []))

    def delete(
        self,
        model_id: str,
        version: str,
    ) -> bool:
        versions = self._versions.get(model_id, [])

        before = len(versions)

        self._versions[model_id] = [
            item
            for item in versions
            if item.version != version
        ]

        return len(self._versions[model_id]) < before