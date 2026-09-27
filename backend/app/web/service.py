from __future__ import annotations

import asyncio
import json
from urllib.parse import quote_plus
from urllib.request import Request, urlopen

from app.core.config import settings
from app.web.schemas import WebSearchResult


class WebSearchService:
    """
    Provider-neutral Internet search layer.

    Preferred provider:
        Tavily

    Development fallback:
        DuckDuckGo Instant Answer API
    """

    def _tavily(
        self,
        query: str,
        limit: int,
    ) -> list[WebSearchResult]:

        if not settings.WEB_SEARCH_API_KEY:
            return []

        payload = json.dumps(
            {
                "api_key": settings.WEB_SEARCH_API_KEY,
                "query": query,
                "max_results": limit,
                "search_depth": (
                    settings.WEB_SEARCH_DEPTH
                ),
            }
        ).encode("utf-8")

        request = Request(
            settings.WEB_SEARCH_API_URL,
            data=payload,
            headers={
                "Content-Type": "application/json",
                "User-Agent": "EVU/1.0",
            },
            method="POST",
        )

        with urlopen(
            request,
            timeout=(
                settings.WEB_SEARCH_TIMEOUT_SECONDS
            ),
        ) as response:

            data = json.loads(
                response.read().decode(
                    "utf-8"
                )
            )

        results: list[
            WebSearchResult
        ] = []

        for item in data.get(
            "results",
            [],
        ):
            url = item.get("url")

            if not url:
                continue

            results.append(
                WebSearchResult(
                    title=item.get(
                        "title",
                        "",
                    ),
                    url=url,
                    snippet=item.get(
                        "content",
                        "",
                    ),
                    source="tavily",
                )
            )

        return results

    def _duckduckgo(
        self,
        query: str,
    ) -> list[WebSearchResult]:

        url = (
            "https://api.duckduckgo.com/"
            "?q="
            + quote_plus(query)
            + "&format=json"
            "&no_html=1"
            "&skip_disambig=1"
        )

        request = Request(
            url,
            headers={
                "User-Agent": "EVU/1.0"
            },
        )

        with urlopen(
            request,
            timeout=(
                settings.WEB_SEARCH_TIMEOUT_SECONDS
            ),
        ) as response:

            data = json.loads(
                response.read().decode(
                    "utf-8"
                )
            )

        results: list[
            WebSearchResult
        ] = []

        abstract_url = data.get(
            "AbstractURL"
        )

        if abstract_url:
            results.append(
                WebSearchResult(
                    title=(
                        data.get(
                            "Heading"
                        )
                        or query
                    ),
                    url=abstract_url,
                    snippet=data.get(
                        "AbstractText",
                        "",
                    ),
                    source="duckduckgo",
                )
            )

        def walk(items):
            for item in items or []:

                first_url = item.get(
                    "FirstURL"
                )

                if first_url:
                    results.append(
                        WebSearchResult(
                            title=item.get(
                                "Text",
                                "",
                            ),
                            url=first_url,
                            snippet=item.get(
                                "Text",
                                "",
                            ),
                            source="duckduckgo",
                        )
                    )

                walk(
                    item.get(
                        "Topics"
                    )
                )

        walk(
            data.get(
                "RelatedTopics"
            )
        )

        return results

    async def search(
        self,
        query: str,
        max_results: int = 5,
    ) -> tuple[
        str,
        list[WebSearchResult],
    ]:

        if not settings.WEB_SEARCH_ENABLED:
            raise RuntimeError(
                "Web search is disabled by "
                "server configuration."
            )

        query = query.strip()

        if not query:
            raise ValueError(
                "Search query cannot be empty."
            )

        max_results = max(
            1,
            min(max_results, 10),
        )

        # Preferred provider.
        try:
            results = await asyncio.to_thread(
                self._tavily,
                query,
                max_results,
            )

            if results:
                return (
                    "tavily",
                    results[:max_results],
                )

        except Exception:
            if not settings.WEB_SEARCH_FALLBACK_ENABLED:
                raise

        # Development fallback.
        try:
            results = await asyncio.to_thread(
                self._duckduckgo,
                query,
            )

            return (
                "duckduckgo",
                results[:max_results],
            )

        except Exception as exc:
            raise RuntimeError(
                f"Web search failed: {exc}"
            ) from exc


web_search_service = WebSearchService()