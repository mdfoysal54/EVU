from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional

from .test_runner import TestResult


@dataclass
class VerificationCheck:
    name: str

    passed: bool

    message: str = ""

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )


@dataclass
class VerificationResult:
    success: bool

    checks: List[
        VerificationCheck
    ] = field(
        default_factory=list
    )

    summary: str = ""

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )

    @property
    def failed_checks(
        self,
    ) -> List[VerificationCheck]:

        return [
            check
            for check in self.checks
            if not check.passed
        ]


class Verifier:
    """
    Final coding-agent verification layer.

    Verification can combine:
        - tests
        - custom checks
        - static checks
        - expected files
        - callback-based verification
    """

    def verify_tests(
        self,
        result: TestResult,
    ) -> VerificationCheck:

        return VerificationCheck(
            name="tests",
            passed=result.success,
            message=(
                "Tests passed."
                if result.success
                else (
                    result.stderr
                    or result.stdout
                    or "Tests failed."
                )
            ),
            metadata={
                "returncode": result.returncode,
                "timed_out": result.timed_out,
                "duration_seconds": (
                    result.duration_seconds
                ),
                "failed_tests": (
                    result.failed_tests
                ),
            },
        )

    def verify_files(
        self,
        filesystem: Any,
        required_files: List[str],
    ) -> VerificationCheck:

        missing = [
            path
            for path in required_files
            if not filesystem.exists(path)
        ]

        return VerificationCheck(
            name="required_files",
            passed=not missing,
            message=(
                "All required files exist."
                if not missing
                else (
                    "Missing files: "
                    + ", ".join(missing)
                )
            ),
            metadata={
                "missing": missing
            },
        )

    def custom(
        self,
        name: str,
        callback: Callable[[], Any],
    ) -> VerificationCheck:

        try:

            result = callback()

            passed = bool(result)

            return VerificationCheck(
                name=name,
                passed=passed,
                message=(
                    "Check passed."
                    if passed
                    else "Check failed."
                ),
                metadata={
                    "result": result
                },
            )

        except Exception as exc:

            return VerificationCheck(
                name=name,
                passed=False,
                message=str(exc),
            )

    def verify(
        self,
        checks: List[
            VerificationCheck
        ],
        *,
        require_all: bool = True,
    ) -> VerificationResult:

        success = (
            all(
                check.passed
                for check in checks
            )
            if require_all
            else any(
                check.passed
                for check in checks
            )
        )

        if success:
            summary = "Verification passed."
        else:
            summary = "Verification failed."

        return VerificationResult(
            success=success,
            checks=checks,
            summary=summary,
        )