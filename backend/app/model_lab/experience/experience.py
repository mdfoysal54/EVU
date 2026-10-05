from __future__ import annotations

import json
import re
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional


def redact_sensitive(text: Optional[str]) -> Optional[str]:
    """Redacts sensitive values like API keys and Bearer tokens."""
    if not text:
        return text

    # Redact Bearer tokens: "Bearer SECRET123" -> "Bearer [REDACTED]"
    text = re.sub(
        r"(Bearer\s+)[^\s\"']+",
        r"\1[REDACTED]",
        text,
        flags=re.IGNORECASE,
    )

    # Redact API keys: "api_key=SECRET" or "api_key: SECRET" -> "api_key=[REDACTED]"
    text = re.sub(
        r"((?:api[_-]?key|apikey)\s*[:=]\s*)[^\s&\"']+",
        r"\1[REDACTED]",
        text,
        flags=re.IGNORECASE,
    )

    return text


@dataclass
class ExperienceRecord:
    prompt: str
    response: Optional[str] = None
    steps: List[Dict[str, Any]] = field(default_factory=list)
    success: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)


class ExperienceStore:
    def __init__(self, file_path: Path | str) -> None:
        self.file_path = Path(file_path)
        self.file_path.parent.mkdir(parents=True, exist_ok=True)

    def append(self, record: ExperienceRecord) -> None:
        with open(self.file_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(asdict(record)) + "\n")

    def load_all(self) -> List[ExperienceRecord]:
        if not self.file_path.exists():
            return []
        records = []
        with open(self.file_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    data = json.loads(line)
                    records.append(ExperienceRecord(**data))
        return records


class RecordingSession:
    def __init__(self, recorder: ExperienceRecorder, prompt: str) -> None:
        self.recorder = recorder
        self.prompt = redact_sensitive(prompt) or ""
        self.response: Optional[str] = None
        self.steps: List[Dict[str, Any]] = []
        self.success: bool = True

    def model_response(self, response: str) -> None:
        self.response = redact_sensitive(response)

    def add_step(self, step: Dict[str, Any]) -> None:
        self.steps.append(step)

    def finish(self, success: bool = True) -> ExperienceRecord:
        self.success = success
        record = ExperienceRecord(
            prompt=self.prompt,
            response=self.response,
            steps=self.steps,
            success=self.success,
        )
        self.recorder.store.append(record)
        return record


class ExperienceRecorder:
    def __init__(self, store: ExperienceStore) -> None:
        self.store = store

    def start(self, prompt: str) -> RecordingSession:
        return RecordingSession(self, prompt)