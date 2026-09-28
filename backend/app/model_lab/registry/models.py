from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, Iterable, Optional
from datetime import datetime, timezone
import uuid


class ModelStatus(str, Enum):
    DEVELOPMENT = "development"
    TESTING = "testing"
    STAGING = "staging"
    PRODUCTION = "production"
    ARCHIVED = "archived"


@dataclass
class ModelMetadata:
    parameter_count: Optional[int] = None
    architecture: Optional[str] = None
    context_length: Optional[int] = None
    tokenizer: Optional[str] = None
    framework: Optional[str] = None
    provider: Optional[str] = None
    tags: list[str] = field(default_factory=list)
    extra: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ModelRecord:
    name: str
    model_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    description: str = ""
    status: ModelStatus = ModelStatus.DEVELOPMENT
    metadata: ModelMetadata = field(default_factory=ModelMetadata)
    current_version: Optional[str] = None
    created_at: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    updated_at: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    def touch(self) -> None:
        self.updated_at = datetime.now(timezone.utc)


class ModelRegistry:
    """
    In-memory registry.

    This provides the application-level API first. It can later be
    backed by PostgreSQL without changing callers significantly.
    """

    def __init__(self) -> None:
        self._models: Dict[str, ModelRecord] = {}

    def register(self, model: ModelRecord) -> ModelRecord:
        model.touch()
        self._models[model.model_id] = model
        return model

    def create(
        self,
        name: str,
        description: str = "",
        metadata: Optional[ModelMetadata] = None,
    ) -> ModelRecord:
        model = ModelRecord(
            name=name,
            description=description,
            metadata=metadata or ModelMetadata(),
        )

        return self.register(model)

    def get(self, model_id: str) -> Optional[ModelRecord]:
        return self._models.get(model_id)

    def get_by_name(self, name: str) -> Optional[ModelRecord]:
        for model in self._models.values():
            if model.name == name:
                return model

        return None

    def update_status(
        self,
        model_id: str,
        status: ModelStatus,
    ) -> ModelRecord:
        model = self._require(model_id)
        model.status = status
        model.touch()
        return model

    def set_current_version(
        self,
        model_id: str,
        version: str,
    ) -> ModelRecord:
        model = self._require(model_id)
        model.current_version = version
        model.touch()
        return model

    def list(
        self,
        status: Optional[ModelStatus] = None,
    ) -> list[ModelRecord]:
        models = list(self._models.values())

        if status is not None:
            models = [
                model
                for model in models
                if model.status == status
            ]

        return sorted(
            models,
            key=lambda item: item.updated_at,
            reverse=True,
        )

    def delete(self, model_id: str) -> bool:
        return self._models.pop(model_id, None) is not None

    def _require(self, model_id: str) -> ModelRecord:
        model = self.get(model_id)

        if model is None:
            raise KeyError(f"Model not found: {model_id}")

        return model

    def __len__(self) -> int:
        return len(self._models)