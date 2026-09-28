from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Dict, Optional
import subprocess
import tempfile
from pathlib import Path


@dataclass
class CodeEvaluationResult:
    passed: bool
    score: float
    output: str = ""
    error: str = ""
    tests_passed: int = 0
    tests_total: int = 0
    details: Dict[str, Any] = field(default_factory=dict)


class CodingEvaluator:
    """
    Basic coding evaluator.

    Intended for controlled local evaluation. Do not use this class
    to execute untrusted code in the EVU production server.
    """

    def __init__(
        self,
        timeout_seconds: int = 10,
    ) -> None:
        self.timeout_seconds = timeout_seconds

    def compare_output(
        self,
        actual: str,
        expected: str,
    ) -> CodeEvaluationResult:
        actual_normalized = actual.strip()
        expected_normalized = expected.strip()

        passed = actual_normalized == expected_normalized

        return CodeEvaluationResult(
            passed=passed,
            score=1.0 if passed else 0.0,
            output=actual,
            details={
                "expected": expected,
                "actual": actual,
            },
        )

    def run_python(
        self,
        source: str,
        expected_output: Optional[str] = None,
    ) -> CodeEvaluationResult:
        temp_path: Optional[Path] = None

        try:
            with tempfile.NamedTemporaryFile(
                mode="w",
                suffix=".py",
                delete=False,
                encoding="utf-8",
            ) as handle:
                handle.write(source)
                temp_path = Path(handle.name)

            process = subprocess.run(
                ["python", str(temp_path)],
                capture_output=True,
                text=True,
                timeout=self.timeout_seconds,
            )

            output = process.stdout.strip()
            error = process.stderr.strip()

            if process.returncode != 0:
                return CodeEvaluationResult(
                    passed=False,
                    score=0.0,
                    output=output,
                    error=error,
                    details={
                        "return_code": process.returncode,
                    },
                )

            if expected_output is not None:
                return self.compare_output(output, expected_output)

            return CodeEvaluationResult(
                passed=True,
                score=1.0,
                output=output,
            )

        except subprocess.TimeoutExpired:
            return CodeEvaluationResult(
                passed=False,
                score=0.0,
                error="Execution timed out.",
            )

        except Exception as exc:
            return CodeEvaluationResult(
                passed=False,
                score=0.0,
                error=str(exc),
            )

        finally:
            if temp_path is not None:
                try:
                    temp_path.unlink(missing_ok=True)
                except OSError:
                    pass

    @staticmethod
    def score_test_counts(
        passed: int,
        total: int,
    ) -> float:
        if total <= 0:
            return 0.0

        return max(0.0, min(1.0, passed / total))