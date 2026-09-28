from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Dict, Iterable, List

from .context import PipelineContext


class ValidationError(Exception):
    """Raised when pipeline validation fails."""


Validator = Callable[[Any, PipelineContext], bool]


@dataclass
class ValidationRule:
    name: str
    validator: Validator
    message: str = "Validation failed."

    def validate(
        self,
        value: Any,
        context: PipelineContext,
    ) -> None:

        try:
            valid = self.validator(value, context)
        except Exception as exc:
            raise ValidationError(
                f"{self.name}: validator error: {exc}"
            ) from exc

        if not valid:
            raise ValidationError(
                f"{self.name}: {self.message}"
            )


@dataclass
class ValidatorSet:
    rules: List[ValidationRule] = field(
        default_factory=list
    )

    def add(
        self,
        rule: ValidationRule,
    ) -> "ValidatorSet":

        self.rules.append(rule)
        return self

    def validate(
        self,
        value: Any,
        context: PipelineContext,
    ) -> None:

        errors: List[str] = []

        for rule in self.rules:
            try:
                rule.validate(value, context)
            except ValidationError as exc:
                errors.append(str(exc))

        if errors:
            raise ValidationError(
                "; ".join(errors)
            )


def required() -> ValidationRule:

    return ValidationRule(
        name="required",
        validator=lambda value, _: value is not None,
        message="value is required.",
    )


def instance_of(
    expected_type: type,
) -> ValidationRule:

    return ValidationRule(
        name="type",
        validator=lambda value, _: isinstance(
            value,
            expected_type,
        ),
        message=f"expected {expected_type.__name__}.",
    )


def predicate(
    name: str,
    function: Callable[[Any], bool],
    message: str,
) -> ValidationRule:

    return ValidationRule(
        name=name,
        validator=lambda value, _: function(value),
        message=message,
    )