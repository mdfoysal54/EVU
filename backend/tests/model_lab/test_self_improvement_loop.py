from app.model_lab.self_improvement.loop import (
    SelfImprovementLoop,
)


def test_self_improvement_loop():
    loop = SelfImprovementLoop()

    records = [
        {
            "id": "1",
            "prompt": "Explain Python",
            "response": (
                "Python is a programming "
                "language."
            ),
            "task_type": "general",
            "success": True,
            "evaluation": {
                "score": 0.95
            },
        }
    ]

    selected = (
        loop.collect_and_select(
            records
        )
    )

    assert len(selected) == 1