from __future__ import annotations

from dataclasses import dataclass, asdict
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path


@dataclass
class DatasetManifest:
    name: str
    version: str
    records: int
    tokens: int = 0
    source_hash: str = ""
    created_at: str = ""
    metadata: dict | None = None

    def to_dict(self) -> dict:
        return asdict(self)


def build_manifest(name: str, version: str, records: list[dict], tokens: int = 0, metadata: dict | None = None) -> DatasetManifest:
    blob = json.dumps(records, ensure_ascii=False, sort_keys=True).encode("utf-8")
    return DatasetManifest(
        name=name,
        version=version,
        records=len(records),
        tokens=tokens,
        source_hash=hashlib.sha256(blob).hexdigest(),
        created_at=datetime.now(timezone.utc).isoformat(),
        metadata=metadata or {},
    )


def save_manifest(manifest: DatasetManifest, path: str | Path) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(manifest.to_dict(), indent=2), encoding="utf-8")