from __future__ import annotations

import hashlib
import re


class Deduplicator:
    """
    Two-stage lightweight deduplicator.

    Exact:
        SHA-256 of normalized text.

    Fingerprint:
        token/word shingles hashed into a compact signature.
    """

    def __init__(self, *, shingle_size: int = 5) -> None:
        self.shingle_size = max(2, shingle_size)
        self._exact: set[str] = set()
        self._fingerprints: set[str] = set()

    @staticmethod
    def normalize(text: str) -> str:
        text = text.lower().strip()
        text = re.sub(r"\s+", " ", text)
        return text

    def exact_hash(self, text: str) -> str:
        normalized = self.normalize(text)
        return hashlib.sha256(
            normalized.encode("utf-8")
        ).hexdigest()

    def fingerprint(self, text: str) -> str:
        words = self.normalize(text).split()

        if len(words) <= self.shingle_size:
            payload = " ".join(words)
        else:
            shingles = [
                " ".join(words[i:i + self.shingle_size])
                for i in range(len(words) - self.shingle_size + 1)
            ]

            payload = "|".join(shingles[:128])

        return hashlib.sha256(
            payload.encode("utf-8")
        ).hexdigest()

    def seen(self, text: str) -> bool:
        exact = self.exact_hash(text)

        if exact in self._exact:
            return True

        fingerprint = self.fingerprint(text)

        if fingerprint in self._fingerprints:
            return True

        self._exact.add(exact)
        self._fingerprints.add(fingerprint)

        return False

    def reset(self) -> None:
        self._exact.clear()
        self._fingerprints.clear()

    @property
    def exact_count(self) -> int:
        return len(self._exact)

    @property
    def fingerprint_count(self) -> int:
        return len(self._fingerprints)