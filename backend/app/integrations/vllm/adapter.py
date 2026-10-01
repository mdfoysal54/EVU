from __future__ import annotations

from dataclasses import dataclass
from typing import Any
import json
import urllib.error
import urllib.request


@dataclass(frozen=True)
class VLLMConfig:
    base_url: str = "http://127.0.0.1:8000/v1"
    api_key: str | None = None
    timeout: float = 120.0


class VLLMAdapter:
    """OpenAI-compatible adapter specialized for vLLM."""

    provider = "vllm"

    def __init__(self, config: VLLMConfig | None = None) -> None:
        self.config = config or VLLMConfig()

    def _request(self, path: str, payload: dict[str, Any] | None = None) -> dict[str, Any]:
        data = None if payload is None else json.dumps(payload).encode()
        headers = {"Content-Type": "application/json"}
        if self.config.api_key:
            headers["Authorization"] = f"Bearer {self.config.api_key}"
        request = urllib.request.Request(
            self.config.base_url.rstrip("/") + path,
            data=data, headers=headers,
            method="POST" if data else "GET",
        )
        try:
            with urllib.request.urlopen(request, timeout=self.config.timeout) as response:
                return json.loads(response.read().decode())
        except urllib.error.URLError as exc:
            raise ConnectionError(f"vLLM request failed: {exc}") from exc

    def health(self) -> bool:
        try:
            self.models()
            return True
        except Exception:
            return False

    def models(self) -> list[dict[str, Any]]:
        return list(self._request("/models").get("data", []))

    def chat(self, model: str, messages: list[dict[str, Any]], **kwargs: Any) -> dict[str, Any]:
        return self._request("/chat/completions", {
            "model": model,
            "messages": messages,
            **kwargs,
        })

    def generate(self, model: str, prompt: str, **kwargs: Any) -> dict[str, Any]:
        return self.chat(model, [{"role": "user", "content": prompt}], **kwargs)
