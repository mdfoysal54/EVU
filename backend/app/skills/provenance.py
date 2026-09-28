from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
import uuid


@dataclass
class SkillProvenance:
    skill_name: str

    source: str
    source_type: str = "unknown"

    version: Optional[str] = None

    author: Optional[str] = None

    verified: bool = False

    provenance_id: str = field(
        default_factory=lambda: str(uuid.uuid4())
    )

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )

    created_at: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )


class ProvenanceTracker:
    def __init__(self) -> None:
        self._records: Dict[
            str,
            List[SkillProvenance],
        ] = {}

    def record(
        self,
        provenance: SkillProvenance,
    ) -> SkillProvenance:
        self._records.setdefault(
            provenance.skill_name,
            [],
        ).append(provenance)

        return provenance

    def list(
        self,
        skill_name: str,
    ) -> List[SkillProvenance]:
        return list(
            self._records.get(
                skill_name,
                [],
            )
        )

    def latest(
        self,
        skill_name: str,
    ) -> Optional[SkillProvenance]:
        records = self.list(skill_name)

        if not records:
            return None

        return records[-1]

    def verify(
        self,
        provenance_id: str,
    ) -> bool:
        for records in self._records.values():
            for record in records:
                if record.provenance_id == provenance_id:
                    record.verified = True
                    return True

        return False