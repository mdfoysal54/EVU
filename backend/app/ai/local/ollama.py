from __future__ import annotations

from typing import Any

import httpx

from app.core.config import settings


class OllamaService:
    """
    HTTP client for a local Ollama runtime.

    EVU does not run the model itself.
    Ollama owns model loading and inference.
    """

    def __init__(self) -> None:
        self.base_url = (
            settings.OLLAMA_BASE_URL.rstrip("/")
        )

    async def health(self) -> dict[str, Any]:
        """
        Check whether Ollama is reachable.
        """

        try:
            async with httpx.AsyncClient(
                timeout=settings.OLLAMA_TIMEOUT_SECONDS
            ) as client:

                response = await client.get(
                    self.base_url
                )

                return {
                    "available": response.status_code
                    == 200,
                    "status_code": response.status_code,
                }

        except Exception as exc:

            return {
                "available": False,
                "error": str(exc),
            }

    async def list_models(
        self,
    ) -> list[dict[str, Any]]:
        """
        Return locally available Ollama models.
        """

        try:

            async with httpx.AsyncClient(
                timeout=settings.OLLAMA_TIMEOUT_SECONDS
            ) as client:

                response = await client.get(
                    f"{self.base_url}/api/tags"
                )

                response.raise_for_status()

                data = response.json()

                return data.get(
                    "models",
                    [],
                )

        except Exception:

            return []

    async def chat(
        self,
        model: str,
        messages: list[dict[str, Any]],
        temperature: float | None = None,
        max_tokens: int | None = None,
    ) -> dict[str, Any]:

        payload: dict[str, Any] = {
            "model": model,
            "messages": messages,
            "stream": False,
        }

        options: dict[str, Any] = {}

        if temperature is not None:
            options["temperature"] = temperature

        if max_tokens is not None:
            options["num_predict"] = max_tokens

        if options:
            payload["options"] = options

        async with httpx.AsyncClient(
            timeout=settings.OLLAMA_TIMEOUT_SECONDS
        ) as client:

            response = await client.post(
                f"{self.base_url}/api/chat",
                json=payload,
            )

            response.raise_for_status()

            return response.json()

    async def generate(
        self,
        model: str,
        prompt: str,
        system: str | None = None,
        temperature: float | None = None,
        max_tokens: int | None = None,
    ) -> dict[str, Any]:

        payload: dict[str, Any] = {
            "model": model,
            "prompt": prompt,
            "stream": False,
        }

        if system:
            payload["system"] = system

        options: dict[str, Any] = {}

        if temperature is not None:
            options["temperature"] = temperature

        if max_tokens is not None:
            options["num_predict"] = max_tokens

        if options:
            payload["options"] = options

        async with httpx.AsyncClient(
            timeout=settings.OLLAMA_TIMEOUT_SECONDS
        ) as client:

            response = await client.post(
                f"{self.base_url}/api/generate",
                json=payload,
            )

            response.raise_for_status()

            return response.json()


ollama_service = OllamaService()