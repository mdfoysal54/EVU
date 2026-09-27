from __future__ import annotations

import asyncio
from dataclasses import dataclass

from app.core.config import settings
from app.web.context import (
    WebContext,
    web_context_builder,
)
from app.web.extractor import (
    web_text_extractor,
)
from app.web.fetcher import (
    WebFetchError,
    web_fetcher,
)
from app.web.ranking import (
    web_result_ranker,
)
from app.web.schemas import (
    WebPageResponse,
    WebSearchResult,
)
from app.web.service import (
    web_search_service,
)


@dataclass
class WebResearchResponse:
    query: str
    provider: str
    search_results: list[WebSearchResult]
    pages: list[WebPageResponse]
    context: WebContext


class WebResearchService:
    """
    High-level EVU Internet research service.

    It coordinates:
        search -> ranking -> fetch -> extraction -> context
    """

    async def search(
        self,
        query: str,
        max_results: int = 5,
    ) -> tuple[
        str,
        list[WebSearchResult],
    ]:

        provider, results = (
            await web_search_service.search(
                query=query,
                max_results=max_results,
            )
        )

        ranked = web_result_ranker.rank(
            query=query,
            results=results,
            limit=max_results,
        )

        return provider, ranked

    async def fetch_page(
        self,
        result: WebSearchResult,
    ) -> WebPageResponse:

        try:
            page = await web_fetcher.fetch(
                result.url
            )

            text = web_text_extractor.extract(
                page.content,
                page.content_type,
            )

            title = result.title.strip()

            if not title:
                title = page.final_url

            return WebPageResponse(
                url=result.url,
                final_url=page.final_url,
                title=title,
                status_code=page.status_code,
                content_type=page.content_type,
                text=text,
                success=True,
                error="",
                score=result.score,
            )

        except WebFetchError as exc:
            return WebPageResponse(
                url=result.url,
                final_url=result.url,
                title=result.title,
                status_code=0,
                content_type="",
                text="",
                success=False,
                error=str(exc),
                score=result.score,
            )

        except Exception as exc:
            return WebPageResponse(
                url=result.url,
                final_url=result.url,
                title=result.title,
                status_code=0,
                content_type="",
                text="",
                success=False,
                error=f"Unexpected fetch error: {exc}",
                score=result.score,
            )

    async def research(
        self,
        query: str,
        max_results: int = 5,
        fetch_pages: int = 3,
    ) -> WebResearchResponse:

        if not settings.WEB_SEARCH_ENABLED:
            raise RuntimeError(
                "Web search is disabled by server configuration."
            )

        max_results = max(
            1,
            min(max_results, 10),
        )

        fetch_pages = max(
            0,
            min(fetch_pages, max_results),
        )

        provider, ranked_results = (
            await self.search(
                query=query,
                max_results=max_results,
            )
        )

        selected = ranked_results[
            :fetch_pages
        ]

        pages: list[WebPageResponse] = []

        if selected:
            fetched = await asyncio.gather(
                *[
                    self.fetch_page(result)
                    for result in selected
                ]
            )

            pages.extend(fetched)

        context = (
            web_context_builder.from_fetched_pages(
                query=query,
                pages=pages,
            )
        )

        # If page fetching failed or was disabled,
        # search snippets still provide useful context.
        if not context.text:
            context = (
                web_context_builder.from_search_results(
                    query=query,
                    results=ranked_results,
                )
            )

        return WebResearchResponse(
            query=query,
            provider=provider,
            search_results=ranked_results,
            pages=pages,
            context=context,
        )


web_research_service = WebResearchService()