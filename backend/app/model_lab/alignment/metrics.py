from __future__ import annotations

from dataclasses import dataclass


@dataclass
class AlignmentMetrics:
    """
    Lightweight alignment metrics used by EVU's
    preference-training experiments.
    """

    preference_accuracy: float
    mean_margin: float
    chosen_log_probability: float
    rejected_log_probability: float

    @property
    def separation(self) -> float:
        return (
            self.chosen_log_probability
            - self.rejected_log_probability
        )


def calculate_alignment_metrics(
    *,
    chosen_log_probability: float,
    rejected_log_probability: float,
    preference_accuracy: float,
) -> AlignmentMetrics:
    return AlignmentMetrics(
        preference_accuracy=float(
            preference_accuracy
        ),
        mean_margin=float(
            chosen_log_probability
            - rejected_log_probability
        ),
        chosen_log_probability=float(
            chosen_log_probability
        ),
        rejected_log_probability=float(
            rejected_log_probability
        ),
    )