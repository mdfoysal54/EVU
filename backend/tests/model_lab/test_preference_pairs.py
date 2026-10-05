from app.model_lab.preference.pairs import (
    make_pair,
)


def test_preference_pair():
    pair = make_pair(
        prompt="question",
        candidate_a="good",
        candidate_b="bad",
        score_a=0.9,
        score_b=0.4,
    )

    assert pair is not None
    assert pair.chosen == "good"
    assert pair.rejected == "bad"


def test_small_margin_is_rejected():
    pair = make_pair(
        prompt="question",
        candidate_a="a",
        candidate_b="b",
        score_a=0.51,
        score_b=0.50,
        min_margin=0.05,
    )

    assert pair is None