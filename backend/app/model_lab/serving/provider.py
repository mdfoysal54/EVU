from __future__ import annotations

from collections.abc import AsyncIterator

import asyncio

from ..inference.batching import (
    BatchGenerationRequest,
)

from .service import (
    EVUGenerationRequest,
    EVUModelService,
)


class EVUOwnedProvider:
    """Provider-compatible adapter for EVU's own local model."""

    provider_name = "evu"

    def __init__(
        self,
        service: EVUModelService,
    ) -> None:

        self.service = service

    @staticmethod
    def _messages_to_prompt(
        messages: list[dict],
    ) -> str:

        parts = []

        for message in messages:

            role = str(
                message.get(
                    "role",
                    "user",
                )
            ).capitalize()

            content = str(
                message.get(
                    "content",
                    "",
                )
            )

            parts.append(
                f"{role}: {content}"
            )

        parts.append(
            "Assistant:"
        )

        return "\n".join(
            parts
        )

    async def generate(
        self,
        messages: list[dict],
        model: str | None = None,
    ) -> str:

        prompt = (
            self._messages_to_prompt(
                messages
            )
        )

        return await asyncio.to_thread(
            self.service.generate,
            EVUGenerationRequest(
                prompt=prompt
            ),
        )

    async def stream(
        self,
        messages: list[dict],
        model: str | None = None,
    ) -> AsyncIterator[str]:

        prompt = (
            self._messages_to_prompt(
                messages
            )
        )

        iterator = self.service.stream(
            EVUGenerationRequest(
                prompt=prompt
            )
        )

        for delta in iterator:
            yield delta

    async def generate_batch(
        self,
        messages_batch: list[
            list[dict]
        ],
        model: str | None = None,
    ) -> list[str]:

        requests = [
            BatchGenerationRequest(
                prompt=(
                    self._messages_to_prompt(
                        messages
                    )
                )
            )
            for messages
            in messages_batch
        ]

        return await asyncio.to_thread(
            self.service.generate_batch,
            requests,
        )