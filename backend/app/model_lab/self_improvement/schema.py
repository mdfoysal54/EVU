from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class ImprovementConfig:
    min_quality_score: float = 0.80
    min_success_rate: float = 0.80
    min_examples: int = 20

    run_sft: bool = True
    run_dpo: bool = True
    run_benchmark: bool = True
    allow_auto_promotion: bool = False

    max_regression: float = 0.02


@dataclass
class ImprovementCandidate:
    example_id: str
    prompt: str
    response: str
    task_type: str
    quality_score: float
    success: bool
    metadata: dict = field(
        default_factory=dict
    )