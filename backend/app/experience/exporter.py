from __future__ import annotations

import json
from pathlib import Path
from typing import Iterable, List

from .models import Experience
from .trajectory import Trajectory


class ExperienceExporter:
    """
    Exports EVU experiences to training/evaluation-friendly formats.
    """

    def experience_dict(
        self,
        experience: Experience,
    ) -> dict:

        return experience.to_dict()

    def trajectory_dict(
        self,
        experience: Experience,
    ) -> dict:

        return Trajectory.from_experience(
            experience
        ).to_training_record()

    def export_json(
        self,
        experiences: Iterable[Experience],
        path: str | Path,
        *,
        indent: int = 2,
    ) -> Path:

        path = Path(path)
        path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        payload = [
            self.experience_dict(
                experience
            )
            for experience in experiences
        ]

        path.write_text(
            json.dumps(
                payload,
                indent=indent,
                ensure_ascii=False,
                default=str,
            ),
            encoding="utf-8",
        )

        return path

    def export_jsonl(
        self,
        experiences: Iterable[Experience],
        path: str | Path,
    ) -> Path:

        path = Path(path)
        path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        with path.open(
            "w",
            encoding="utf-8",
        ) as file:

            for experience in experiences:
                file.write(
                    json.dumps(
                        self.experience_dict(
                            experience
                        ),
                        ensure_ascii=False,
                        default=str,
                    )
                    + "\n"
                )

        return path

    def export_training_jsonl(
        self,
        experiences: Iterable[Experience],
        path: str | Path,
    ) -> Path:

        path = Path(path)
        path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        with path.open(
            "w",
            encoding="utf-8",
        ) as file:

            for experience in experiences:

                record = (
                    Trajectory
                    .from_experience(
                        experience
                    )
                    .to_training_record()
                )

                file.write(
                    json.dumps(
                        record,
                        ensure_ascii=False,
                        default=str,
                    )
                    + "\n"
                )

        return path

    def to_json(
        self,
        experience: Experience,
        *,
        indent: int = 2,
    ) -> str:

        return json.dumps(
            self.experience_dict(
                experience
            ),
            indent=indent,
            ensure_ascii=False,
            default=str,
        )