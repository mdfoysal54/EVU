from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, Optional
import uuid


@dataclass
class Artifact:
    name: str
    content: Any
    artifact_type: str = "generic"
    artifact_id: str = field(
        default_factory=lambda: str(uuid.uuid4())
    )
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )


class ArtifactStore:
    def __init__(self) -> None:
        self._artifacts: Dict[str, Artifact] = {}

    def save(self, artifact: Artifact) -> Artifact:
        self._artifacts[artifact.artifact_id] = artifact
        return artifact

    def create(
        self,
        name: str,
        content: Any,
        artifact_type: str = "generic",
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Artifact:
        return self.save(
            Artifact(
                name=name,
                content=content,
                artifact_type=artifact_type,
                metadata=metadata or {},
            )
        )

    def get(self, artifact_id: str) -> Optional[Artifact]:
        return self._artifacts.get(artifact_id)

    def find_by_name(self, name: str) -> list[Artifact]:
        return [
            artifact
            for artifact in self._artifacts.values()
            if artifact.name == name
        ]

    def delete(self, artifact_id: str) -> bool:
        return self._artifacts.pop(
            artifact_id,
            None,
        ) is not None

    def list(self) -> list[Artifact]:
        return list(self._artifacts.values())