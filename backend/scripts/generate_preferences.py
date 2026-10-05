from __future__ import annotations

import argparse
import json
from pathlib import Path

from app.model_lab.preference.pipeline import (
    PreferenceGenerationPipeline,
)


def load_prompts(
    path: Path,
) -> list[str]:
    prompts = []

    with path.open(
        "r",
        encoding="utf-8",
    ) as handle:
        for line in handle:
            line = line.strip()

            if not line:
                continue

            record = json.loads(line)

            prompt = (
                record.get("prompt")
                or record.get("instruction")
                or record.get("input")
            )

            if prompt:
                prompts.append(
                    str(prompt)
                )

    return prompts


def main() -> None:
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--prompts",
        required=True,
    )

    parser.add_argument(
        "--output",
        required=True,
    )

    args = parser.parse_args()

    prompts = load_prompts(
        Path(args.prompts)
    )

    # This CLI intentionally requires
    # a model generator to be supplied
    # by the integration layer.
    #
    # We do NOT silently call OpenAI,
    # Anthropic, Gemini, etc.
    raise SystemExit(
        "Connect --generator to the local "
        "EVU inference service before running "
        "automatic preference generation."
    )


if __name__ == "__main__":
    main()