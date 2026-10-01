from __future__ import annotations

from pathlib import Path


class ModelArtifactStore:
    def __init__(self, root: str | Path) -> None:
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)

    def model_dir(self, model_id: str, version: str) -> Path:
        path = self.root / model_id / version
        path.mkdir(parents=True, exist_ok=True)
        return path

    def checkpoint_path(self, model_id: str, version: str) -> Path:
        return self.model_dir(model_id, version) / "model.pt"