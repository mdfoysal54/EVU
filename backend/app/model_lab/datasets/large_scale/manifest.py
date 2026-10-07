from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


@dataclass
class DatasetManifest:
    name: str
    version: str
    source_count: int
    train_records: int
    validation_records: int
    files: list[str] = field(default_factory=list)
    provenance: list[dict[str, Any]] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)
    created_at: str = field(
        default_factory=lambda: datetime.now(
            timezone.utc
        ).isoformat()
    )

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "version": self.version,
            "source_count": self.source_count,
            "train_records": self.train_records,
            "validation_records": self.validation_records,
            "files": self.files,
            "provenance": self.provenance,
            "metadata": self.metadata,
            "created_at": self.created_at,
        }

    def save(self, path: str | Path) -> None:
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)

        path.write_text(
            json.dumps(
                self.to_dict(),
                indent=2,
                ensure_ascii=False,
            ),
            encoding="utf-8",
        )

    def checksum(self) -> str:
        payload = json.dumps(
            self.to_dict(),
            sort_keys=True,
            ensure_ascii=False,
        )

        return hashlib.sha256(
            payload.encode("utf-8")
        ).hexdigest()