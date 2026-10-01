from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import threading

import torch

from ..inference.batching import (
    BatchGenerationRequest,
    generate_batch,
)

from ..inference.engine import (
    EVUInferenceEngine,
    GenerationConfig,
)

from ..inference.quantization import (
    prepare_inference_dtype,
    quantize_dynamic_int8,
)

from ..inference.streaming import (
    stream_generate,
)

from .bundle import EVUModelBundle


@dataclass
class EVUGenerationRequest:

    prompt: str

    max_new_tokens: int = 128

    temperature: float = 0.7

    top_k: int | None = 50

    top_p: float = 0.95

    greedy: bool = False

    use_cache: bool = True


class EVUModelService:
    """Process-local owned-model service."""

    def __init__(
        self,
        bundle_dir: str | Path,
        *,
        device: str = "cpu",
        quantization: str = "none",
    ) -> None:

        self.bundle_dir = Path(
            bundle_dir
        )

        self.device = device

        self.quantization = (
            quantization or "none"
        ).lower()

        self._bundle = None

        self._engine = None

        self._lock = (
            threading.Lock()
        )

    @property
    def loaded(self) -> bool:

        return (
            self._bundle is not None
            and self._engine is not None
        )

    def load(self) -> None:

        with self._lock:

            if self.loaded:
                return

            bundle = (
                EVUModelBundle.load(
                    self.bundle_dir,
                    device=self.device,
                )
            )

            model = bundle.model

            if (
                self.quantization
                == "int8"
            ):

                if (
                    torch.device(
                        self.device
                    ).type
                    != "cpu"
                ):
                    raise ValueError(
                        "int8 dynamic "
                        "quantization is CPU-only"
                    )

                model = (
                    quantize_dynamic_int8(
                        model
                    )
                )

            elif self.quantization in {
                "none",
                "",
                "auto",
            }:

                if (
                    self.quantization
                    == "auto"
                ):

                    model = (
                        prepare_inference_dtype(
                            model,
                            self.device,
                        )
                    )

            else:

                raise ValueError(
                    "Unsupported "
                    "EVU_MODEL_QUANTIZATION="
                    f"{self.quantization!r}; "
                    "use none, auto, or int8"
                )

            model.eval()

            bundle.model = model

            self._bundle = bundle

            self._engine = (
                EVUInferenceEngine(
                    model,
                    bundle.tokenizer,
                    device=self.device,
                )
            )

    def unload(self) -> None:

        with self._lock:

            self._engine = None

            self._bundle = None

            if torch.cuda.is_available():
                torch.cuda.empty_cache()

    def status(self) -> dict:

        return {
            "loaded": self.loaded,
            "bundle_dir": str(
                self.bundle_dir
            ),
            "device": self.device,
            "quantization": (
                self.quantization
            ),
            "kv_cache": True,
            "sdpa": hasattr(
                torch.nn.functional,
                "scaled_dot_product_attention",
            ),
        }

    def _require_engine(
        self,
    ) -> EVUInferenceEngine:

        self.load()

        assert self._engine is not None

        return self._engine

    def generate(
        self,
        request: EVUGenerationRequest,
    ) -> str:

        if not request.prompt.strip():
            raise ValueError(
                "prompt must not be empty."
            )

        engine = (
            self._require_engine()
        )

        assert self._bundle is not None

        prompt_ids = (
            self._bundle.tokenizer.encode(
                request.prompt,
                add_special_tokens=True,
            )
        )

        input_tensor = torch.tensor(
            [prompt_ids],
            dtype=torch.long,
            device=self.device,
        )

        output_ids = (
            engine.generate_ids(
                input_tensor,
                GenerationConfig(
                    max_new_tokens=(
                        request.max_new_tokens
                    ),
                    temperature=(
                        request.temperature
                    ),
                    top_k=request.top_k,
                    top_p=request.top_p,
                    greedy=request.greedy,
                    eos_token_id=(
                        self._bundle.tokenizer
                        .eos_token_id
                    ),
                    use_cache=(
                        request.use_cache
                    ),
                ),
            )
        )

        completion_ids = (
            output_ids[0]
            .tolist()
            [len(prompt_ids):]
        )

        return (
            self._bundle.tokenizer.decode(
                completion_ids,
                skip_special_tokens=True,
            )
            .strip()
        )

    def stream(
        self,
        request: EVUGenerationRequest,
    ):

        if not request.prompt.strip():
            raise ValueError(
                "prompt must not be empty."
            )

        self.load()

        assert self._bundle is not None

        yield from stream_generate(
            self._bundle.model,
            self._bundle.tokenizer,
            request.prompt,
            config=GenerationConfig(
                max_new_tokens=(
                    request.max_new_tokens
                ),
                temperature=(
                    request.temperature
                ),
                top_k=request.top_k,
                top_p=request.top_p,
                greedy=request.greedy,
                eos_token_id=(
                    self._bundle.tokenizer
                    .eos_token_id
                ),
                use_cache=(
                    request.use_cache
                ),
            ),
        )

    def generate_batch(
        self,
        requests: list[
            BatchGenerationRequest
        ],
    ) -> list[str]:

        if not requests:
            return []

        self.load()

        assert self._bundle is not None

        tokenizer = (
            self._bundle.tokenizer
        )

        encoded = [
            tokenizer.encode(
                request.prompt,
                add_special_tokens=True,
            )
            for request in requests
        ]

        first = requests[0]

        different_settings = any(
            (
                request.max_new_tokens
                != first.max_new_tokens
                or request.temperature
                != first.temperature
                or request.top_k
                != first.top_k
                or request.top_p
                != first.top_p
                or request.greedy
                != first.greedy
            )
            for request in requests[1:]
        )

        if different_settings:
            raise ValueError(
                "All batch requests must "
                "use the same generation settings"
            )

        outputs = generate_batch(
            self._bundle.model,
            encoded,
            pad_token_id=(
                tokenizer.pad_token_id
            ),
            eos_token_id=(
                tokenizer.eos_token_id
            ),
            max_new_tokens=(
                first.max_new_tokens
            ),
            temperature=(
                first.temperature
            ),
            top_k=first.top_k,
            top_p=first.top_p,
            greedy=first.greedy,
            use_cache=True,
        )

        results = []

        for original_ids, output_ids in zip(
            encoded,
            outputs,
        ):

            completion_ids = (
                output_ids[
                    len(original_ids):
                ]
            )

            results.append(
                tokenizer.decode(
                    completion_ids,
                    skip_special_tokens=True,
                ).strip()
            )

        return results