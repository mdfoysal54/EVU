from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Iterable
from uuid import uuid4

from .provenance import ResearchSource


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class VerificationStatus(str, Enum):
    UNCHECKED = "unchecked"
    SUPPORTED = "supported"
    PARTIALLY_SUPPORTED = "partially_supported"
    CONTRADICTED = "contradicted"
    INCONCLUSIVE = "inconclusive"


@dataclass
class VerificationCheck:
    source_id: str
    status: VerificationStatus
    notes: str = ""
    checked_at: datetime = field(default_factory=utcnow)
    checker: str = "evu"
    id: str = field(default_factory=lambda: str(uuid4()))


@dataclass
class VerificationResult:
    claim: str
    status: VerificationStatus
    confidence: float
    checks: list[VerificationCheck] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)


class ResearchVerifier:
    """Deterministic evidence verifier; semantic verification can be injected."""

    def __init__(self, semantic_checker=None) -> None:
        self.semantic_checker = semantic_checker

    @staticmethod
    def _contains_claim(claim: str, source: ResearchSource) -> bool:
        if not claim.strip() or not source.content:
            return False
        claim_words = {
            word.lower().strip(".,!?;:")
            for word in claim.split()
            if len(word) > 3
        }
        source_words = {
            word.lower().strip(".,!?;:")
            for word in source.content.split()
        }
        if not claim_words:
            return False
        return len(claim_words & source_words) / len(claim_words) >= 0.6

    def verify(
        self,
        claim: str,
        sources: Iterable[ResearchSource],
    ) -> VerificationResult:
        sources = list(sources)
        checks: list[VerificationCheck] = []

        for source in sources:
            if self.semantic_checker:
                try:
                    raw = self.semantic_checker(claim, source)
                    if isinstance(raw, tuple):
                        status, notes = raw
                    else:
                        status, notes = raw, ""
                    status = VerificationStatus(status)
                except Exception as exc:
                    status = VerificationStatus.INCONCLUSIVE
                    notes = f"Semantic checker failed: {exc}"
            else:
                status = (
                    VerificationStatus.SUPPORTED
                    if self._contains_claim(claim, source)
                    else VerificationStatus.INCONCLUSIVE
                )
                notes = "Lexical baseline check."

            checks.append(
                VerificationCheck(
                    source_id=source.id,
                    status=status,
                    notes=notes,
                )
            )

        supported = sum(c.status == VerificationStatus.SUPPORTED for c in checks)
        contradicted = sum(c.status == VerificationStatus.CONTRADICTED for c in checks)

        if contradicted and supported:
            status = VerificationStatus.PARTIALLY_SUPPORTED
        elif contradicted:
            status = VerificationStatus.CONTRADICTED
        elif supported:
            status = VerificationStatus.SUPPORTED
        else:
            status = VerificationStatus.INCONCLUSIVE

        confidence = 0.0
        if checks:
            confidence = min(1.0, supported / len(checks))
            if contradicted:
                confidence *= 0.5

        return VerificationResult(
            claim=claim,
            status=status,
            confidence=confidence,
            checks=checks,
        )
