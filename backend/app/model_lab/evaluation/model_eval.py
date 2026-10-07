from __future__ import annotations

from dataclasses import dataclass


@dataclass
class ModelEvaluation:
    model_id: str
    version: str
    benchmark_score: float
    pass_rate: float
    latency: float
    perplexity: float | None = None
    safety_score: float | None = None

    def deployment_score(
        self,
    ) -> float:
        components = [
            self.benchmark_score,
            self.pass_rate,
        ]

        if self.safety_score is not None:
            components.append(
                self.safety_score
            )

        return sum(components) / len(
            components
        )

    def to_dict(self) -> dict:
        return {
            "model_id": self.model_id,
            "version": self.version,
            "benchmark_score": (
                self.benchmark_score
            ),
            "pass_rate": self.pass_rate,
            "latency": self.latency,
            "perplexity": self.perplexity,
            "safety_score": (
                self.safety_score
            ),
            "deployment_score": (
                self.deployment_score()
            ),
        }