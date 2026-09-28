from __future__ import annotations

from .models import DiagramRequestModel, DiagramResult
from .planner import DiagramPlanner
from .types import BUILDERS
from .validator import DiagramValidator


class DiagramService:
    """
    Main application service for EVU's diagram subsystem.

    Pipeline:

        prompt
          ↓
        planner
          ↓
        type selection
          ↓
        diagram builder
          ↓
        IR
          ↓
        validator
          ↓
        result
    """

    def __init__(
        self,
        planner: DiagramPlanner | None = None,
        validator: DiagramValidator | None = None,
    ) -> None:
        self.planner = planner or DiagramPlanner()
        self.validator = validator or DiagramValidator()

    def generate(
        self,
        request: DiagramRequestModel,
    ) -> DiagramResult:
        plan = self.planner.plan(
            request.prompt,
            request.diagram_type,
        )

        builder = BUILDERS.get(plan.diagram_type)

        if builder is None:
            raise ValueError(
                f"No builder registered for diagram type "
                f"'{plan.diagram_type}'."
            )

        diagram = builder(
            request.prompt,
            request.title,
        )

        diagram.direction = plan.direction

        diagram.metadata.update(
            {
                "planner_confidence": plan.confidence,
                "reasoning": plan.reasoning,
            }
        )

        validation = self.validator.validate(diagram)

        if not validation.valid:
            raise ValueError(
                "Generated diagram failed validation: "
                + "; ".join(validation.errors)
            )

        return DiagramResult(
            diagram=diagram,
            plan=plan,
            warnings=validation.warnings,
        )

    def generate_from_prompt(
        self,
        prompt: str,
        diagram_type: str | None = None,
        title: str | None = None,
    ) -> DiagramResult:
        request = DiagramRequestModel(
            prompt=prompt,
            diagram_type=diagram_type,
            title=title,
        )

        return self.generate(request)

    def supported_types(self) -> list[str]:
        return sorted(BUILDERS.keys())


diagram_service = DiagramService()