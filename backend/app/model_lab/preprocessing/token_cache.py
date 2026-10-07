from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


class AdvancedTokenCache:
    def __init__(
        self,
        directory: str | Path,
    ) -> None:
        self.directory = Path(directory)
        self.directory.mkdir(
            parents=True,
            exist_ok=True,
        )

    def _key(
        self,
        text: str,
        *,
        tokenizer_version: str,
        max_length: int | None,
    ) -> str:
        payload = json.dumps(
            {
                "text": text,
                "tokenizer_version": tokenizer_version,
                "max_length": max_length,
            },
            sort_keys=True,
            ensure_ascii=False,
        )

        return hashlib.sha256(
            payload.encode("utf-8")
        ).hexdigest()

    def get(
        self,
        text: str,
        *,
        tokenizer_version: str,
        max_length: int | None,
    ) -> list[int] | None:
        key = self._key(
            text,
            tokenizer_version=tokenizer_version,
            max_length=max_length,
        )

        path = self.directory / f"{key}.json"

        if not path.exists():
            return None

        return json.loads(
            path.read_text(
                encoding="utf-8"
            )
        )

    def set(
        self,
        text: str,
        tokens: list[int],
        *,
        tokenizer_version: str,
        max_length: int | None,
    ) -> None:
        key = self._key(
            text,
            tokenizer_version=tokenizer_version,
            max_length=max_length,
        )

        path = self.directory / f"{key}.json"

        path.write_text(
            json.dumps(tokens),
            encoding="utf-8",
        )