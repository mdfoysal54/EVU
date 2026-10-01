from __future__ import annotations

import traceback
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional


@dataclass
class DebugResult:
    success: bool

    result: Any = None

    error_type: Optional[str] = None
    error_message: Optional[str] = None

    traceback_text: Optional[
        str
    ] = None

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )


class Debugger:
    """
    Lightweight Python execution debugger.

    It does not attempt to replace a full IDE debugger.

    Its purpose is to give EVU structured failure information that
    can be fed back into the coding agent.
    """

    def run(
        self,
        function: Callable[..., Any],
        *args: Any,
        **kwargs: Any,
    ) -> DebugResult:

        try:

            result = function(
                *args,
                **kwargs,
            )

            return DebugResult(
                success=True,
                result=result,
            )

        except Exception as exc:

            return DebugResult(
                success=False,
                error_type=type(
                    exc
                ).__name__,
                error_message=str(
                    exc
                ),
                traceback_text=traceback.format_exc(),
            )

    def analyze_output(
        self,
        output: str,
    ) -> Dict[str, Any]:

        lines = output.splitlines()

        errors: List[str] = []

        for line in lines:

            lowered = line.lower()

            if (
                "error" in lowered
                or "exception" in lowered
                or "traceback" in lowered
                or "failed" in lowered
            ):
                errors.append(
                    line.strip()
                )

        return {
            "has_error": bool(errors),
            "error_lines": errors,
            "line_count": len(lines),
        }

    def extract_exception(
        self,
        traceback_text: str,
    ) -> Dict[str, Optional[str]]:

        lines = [
            line.strip()
            for line
            in traceback_text.splitlines()
            if line.strip()
        ]

        if not lines:
            return {
                "type": None,
                "message": None,
            }

        last = lines[-1]

        if ":" in last:
            error_type, message = (
                last.split(
                    ":",
                    1,
                )
            )

            return {
                "type": error_type.strip(),
                "message": message.strip(),
            }

        return {
            "type": last,
            "message": None,
        }