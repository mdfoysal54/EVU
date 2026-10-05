from app.model_lab.preference.generation import (
    generate_candidates,
)


def test_candidate_generation():
    calls = []

    def generator(prompt):
        calls.append(prompt)

        return (
            f"Answer to {prompt}"
        )

    candidates = generate_candidates(
        "hello",
        generator,
        count=3,
    )

    assert len(candidates) == 3
    assert len(calls) == 3