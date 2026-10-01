from __future__ import annotations

import json
import urllib.error
import urllib.request
from dataclasses import dataclass
from typing import Any, Iterator


@dataclass(frozen=True)
class OllamaConfig:
    base_url: str = "http://127.0.0.1:11434"
    timeout: float = 120.0


class OllamaAdapter:
    """Provider adapter for the Ollama HTTP API."""

    provider = "ollama"

    def __init__(self, config: OllamaConfig | None = None) -> None:
        self.config = config or OllamaConfig()

    def _request(self, path: str, payload: dict[str, Any] | None = None) -> dict[str, Any]:
        data = None if payload is None else json.dumps(payload).encode()
        request = urllib.request.Request(
            self.config.base_url.rstrip("/") + path,
            data=data,
            headers={"Content-Type": "application/json"},
            method="POST" if data else "GET",
        )
        try:
            with urllib.request.urlopen(request, timeout=self.config.timeout) as response:
                return json.loads(response.read().decode())
        except urllib.error.URLError as exc:
            raise ConnectionError(f"Ollama request failed: {exc}") from exc

    def health(self) -> bool:
        try:
            self._request("/api/tags")
            return True
        except Exception:
            return False

    def models(self) -> list[dict[str, Any]]:
        return list(self._request("/api/tags").get("models", []))

    def generate(self, model: str, prompt: str, **options: Any) -> dict[str, Any]:
        return self._request("/api/generate", {
            "model": model,
            "prompt": prompt,
            "stream": False,
            "options": options,
        })

    def chat(self, model: str, messages: list[dict[str, str]], **options: Any) -> dict[str, Any]:
        return self._request("/api/chat", {
            "model": model,
            "messages": messages,
            "stream": False,
            "options": options,
        })
