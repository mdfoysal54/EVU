from __future__ import annotations

from app.model_lab.experience.schema import (
    ExperienceRecord,
)

from .schema import ToolUseExample


def build_tool_use_dataset(
    experiences: list[ExperienceRecord],
    minimum_score: float = 0.75,
) -> list[ToolUseExample]:

    output = []

    for experience in experiences:

        if not experience.evaluation:
            continue

        score = (
            experience.evaluation.overall
        )

        if score < minimum_score:
            continue

        trajectory = experience.metadata.get(
            "trajectory",
            {},
        )

        steps = trajectory.get(
            "steps",
            [],
        )

        for step in steps:

            tool_name = step.get(
                "tool_name"
            )

            if not tool_name:
                continue

            arguments = step.get(
                "action_input"
            )

            result = step.get(
                "observation"
            )

            success = step.get(
                "tool_success",
                True,
            )

            output.append(
                ToolUseExample(
                    example_id=(
                        f"{experience.experience_id}"
                        f"-tool-{step.get('step_id')}"
                    ),
                    prompt=experience.prompt,
                    response=experience.response,
                    tool_name=tool_name,
                    tool_arguments=(
                        arguments
                        if isinstance(
                            arguments,
                            dict,
                        )
                        else {}
                    ),
                    tool_result=result,
                    tool_success=bool(
                        success
                    ),
                    quality_score=score,
                    metadata={
                        "source":
                            "evu_experience",
                        "experience_id":
                            experience.experience_id,
                    },
                )
            )

    return output