from __future__ import annotations

import hashlib
import re


class ExactDeduplicator:
    def __init__(self) -> None:
        self._seen: set[str] = set()

    @staticmethod
    def fingerprint(text: str) -> str:
        normalized = re.sub(r"\s+", " ", text.strip()).lower()
        return hashlib.sha256(normalized.encode("utf-8")).hexdigest()

    def accept(self, text: str) -> bool:
        digest = self.fingerprint(text)
        if digest in self._seen:
            return False
        self._seen.add(digest)
        return True

    def __len__(self) -> int:
        return len(self._seen)