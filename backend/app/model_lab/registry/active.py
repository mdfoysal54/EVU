from __future__ import annotations

import json
from pathlib import Path


class ActiveModelPointer:
    def __init__(
        self,
        path: str | Path,
    ) -> None:
        self.path = Path(path)

        self.path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

    def get(self) -> dict | None:
        if not self.path.exists():
            return None

        return json.loads(
            self.path.read_text(
                encoding="utf-8"
            )
        )

    def set(
        self,
        model_id: str,
        version: str,
    ) -> dict:
        value = {
            "model_id": model_id,
            "version": version,
        }

        self.path.write_text(
            json.dumps(
                value,
                indent=2,
            ),
            encoding="utf-8",
        )

        return value

    def clear(self) -> None:
        self.path.unlink(
            missing_ok=True
        )