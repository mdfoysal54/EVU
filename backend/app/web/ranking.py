from __future__ import annotations

import re
from urllib.parse import urlparse

from app.web.schemas import WebSearchResult


class WebResultRanker:
    """
    Deterministic search-result ranker.

    This is intentionally lightweight.

    Later EVU can replace or extend this with:
    - cross-encoder ranking
    - embedding similarity
    - learned ranking
    - source authority models
    """

    TRUSTED_DOMAINS = {
        "python.org",
        "docs.python.org",
        "fastapi.tiangolo.com",
        "github.com",
        "developer.mozilla.org",
        "wikipedia.org",
        "arxiv.org",
        "ietf.org",
        "w3.org",
    }

    STOP_WORDS = {
        "the",
        "a",
        "an",
        "is",
        "are",
        "was",
        "were",
        "to",
        "of",
        "in",
        "on",
        "for",
        "with",
        "and",
        "or",
        "how",
        "what",
        "why",
        "when",
        "where",
        "which",
        "who",
        "this",
        "that",
        "from",
        "about",
    }

    @staticmethod
    def _tokenize(text: str) -> set[str]:
        tokens = re.findall(
            r"[a-zA-Z0-9_]+",
            text.lower(),
        )

        return {
            token
            for token in tokens
            if token not in WebResultRanker.STOP_WORDS
            and len(token) > 1
        }

    @staticmethod
    def _domain(url: str) -> str:
        try:
            hostname = (
                urlparse(url)
                .hostname
                or ""
            ).lower()

            if hostname.startswith("www."):
                hostname = hostname[4:]

            return hostname

        except Exception:
            return ""

    @classmethod
    def _domain_score(cls, url: str) -> float:
        domain = cls._domain(url)

        if not domain:
            return 0.0

        if domain in cls.TRUSTED_DOMAINS:
            return 0.25

        for trusted in cls.TRUSTED_DOMAINS:
            if domain.endswith(
                "." + trusted
            ):
                return 0.20

        return 0.0

    @classmethod
    def score(
        cls,
        query: str,
        result: WebSearchResult,
        original_position: int = 0,
    ) -> float:

        query_tokens = cls._tokenize(query)

        title_tokens = cls._tokenize(
            result.title
        )

        snippet_tokens = cls._tokenize(
            result.snippet
        )

        if not query_tokens:
            return 0.0

        title_overlap = (
            len(
                query_tokens
                & title_tokens
            )
            / len(query_tokens)
        )

        snippet_overlap = (
            len(
                query_tokens
                & snippet_tokens
            )
            / len(query_tokens)
        )

        score = 0.0

        # Title is stronger than snippet.
        score += title_overlap * 0.55
        score += snippet_overlap * 0.25

        # Trusted domain bonus.
        score += cls._domain_score(
            result.url
        )

        # HTTPS bonus.
        if result.url.lower().startswith(
            "https://"
        ):
            score += 0.05

        # Earlier search results get a small advantage.
        if original_position >= 0:
            position_bonus = max(
                0.0,
                0.10
                - (original_position * 0.01),
            )
            score += position_bonus

        return round(
            min(score, 1.0),
            4,
        )

    @classmethod
    def rank(
        cls,
        query: str,
        results: list[WebSearchResult],
        limit: int = 10,
    ) -> list[WebSearchResult]:

        if not results:
            return []

        ranked: list[
            tuple[float, int, WebSearchResult]
        ] = []

        seen_urls: set[str] = set()

        for position, result in enumerate(
            results
        ):
            normalized_url = (
                result.url.strip().lower().rstrip("/")
            )

            if not normalized_url:
                continue

            if normalized_url in seen_urls:
                continue

            seen_urls.add(normalized_url)

            score = cls.score(
                query,
                result,
                position,
            )

            # Pydantic model is intentionally copied
            # rather than mutated in-place.
            ranked.append(
                (
                    score,
                    position,
                    result.model_copy(
                        update={
                            "score": score
                        }
                    ),
                )
            )

        ranked.sort(
            key=lambda item: (
                -item[0],
                item[1],
            )
        )

        return [
            item[2]
            for item in ranked[:limit]
        ]


web_result_ranker = WebResultRanker()