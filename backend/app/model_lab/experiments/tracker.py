from __future__ import annotations

from dataclasses import dataclass, asdict
from datetime import datetime, timezone
import json
from pathlib import Path
import uuid


@dataclass
class ExperimentRun:
    run_id: str
    name: str
    config: dict
    metrics: dict
    created_at: str


class ExperimentTracker:
    def __init__(self, root: str | Path) -> None:
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)

    def start(self, name: str, config: dict | None = None) -> ExperimentRun:
        run = ExperimentRun(
            run_id=str(uuid.uuid4()),
            name=name,
            config=config or {},
            metrics={},
            created_at=datetime.now(timezone.utc).isoformat(),
        )
        self._write(run)
        return run

    def log_metrics(self, run: ExperimentRun, **metrics: float) -> ExperimentRun:
        run.metrics.update({k: float(v) for k, v in metrics.items()})
        self._write(run)
        return run

    def _write(self, run: ExperimentRun) -> None:
        path = self.root / f"{run.run_id}.json"
        path.write_text(json.dumps(asdict(run), indent=2), encoding="utf-8")