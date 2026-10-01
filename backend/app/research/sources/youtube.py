from __future__ import annotations

from dataclasses import dataclass
from urllib.parse import urlparse, parse_qs

from ..provenance import EvidenceType, ResearchSource


@dataclass
class YouTubeSourceConfig:
    timeout: float = 20.0


class YouTubeSource:
    """YouTube metadata/transcript adapter using an injected provider."""

    def __init__(self, config: YouTubeSourceConfig | None = None, provider=None) -> None:
        self.config = config or YouTubeSourceConfig()
        self.provider = provider

    @staticmethod
    def video_id(url: str) -> str | None:
        parsed = urlparse(url)
        if parsed.netloc.endswith("youtu.be"):
            return parsed.path.strip("/") or None
        if "youtube.com" in parsed.netloc:
            return parse_qs(parsed.query).get("v", [None])[0]
        return None

    def fetch(self, url: str) -> ResearchSource:
        video_id = self.video_id(url)
        if not video_id:
            raise ValueError("Invalid YouTube URL")
        if self.provider is None:
            raise RuntimeError("No YouTube provider configured")

        data = self.provider(video_id)
        if not isinstance(data, dict):
            data = {"transcript": str(data)}

        transcript = str(data.get("transcript") or "")
        title = str(data.get("title") or "YouTube video")

        return ResearchSource(
            url=url,
            title=title,
            source_type="youtube",
            publisher="YouTube",
            author=str(data.get("channel") or ""),
            content=transcript,
            snippet=transcript[:500],
            evidence_type=EvidenceType.SECONDARY,
            metadata=data,
        )
