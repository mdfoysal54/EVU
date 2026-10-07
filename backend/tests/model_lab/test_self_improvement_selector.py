from app.model_lab.self_improvement.schema import (
    ImprovementCandidate,
    ImprovementConfig,
)
from app.model_lab.self_improvement.selector import (
    ExperienceSelector,
)


def test_selector():
    selector = ExperienceSelector(
        ImprovementConfig(
            min_quality_score=0.8
        )
    )

    examples = [
        ImprovementCandidate(
            example_id="1",
            prompt="good",
            response="good answer",
            task_type="general",
            quality_score=0.95,
            success=True,
        ),
        ImprovementCandidate(
            example_id="2",
            prompt="bad",
            response="bad answer",
            task_type="general",
            quality_score=0.2,
            success=True,
        ),
    ]

    selected = selector.select(
        examples
    )

    assert len(selected) == 1
    assert selected[0].example_id == "1"