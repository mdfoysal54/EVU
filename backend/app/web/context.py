from __future__ import annotations

from dataclasses import dataclass

from app.web.schemas import WebPageResponse, WebSearchResult


@dataclass
class WebContext:
    query: str
    text: str
    sources: list[WebSearchResult]


class WebContextBuilder:
    """
    Converts web search/fetched-page information into
    bounded model context.
    """

    def __init__(
        self,
        max_context_chars: int = 12_000,
        max_source_chars: int = 3_000,
    ):
        self.max_context_chars = max_context_chars
        self.max_source_chars = max_source_chars

    @staticmethod
    def _source_header(
        index: int,
        title: str,
        url: str,
    ) -> str:
        return (
            f"[SOURCE {index}]\n"
            f"Title: {title}\n"
            f"URL: {url}\n"
        )

    def from_search_results(
        self,
        query: str,
        results: list[WebSearchResult],
    ) -> WebContext:

        blocks: list[str] = []
        selected: list[WebSearchResult] = []

        total_chars = 0

        for index, result in enumerate(
            results,
            start=1,
        ):
            snippet = (
                result.snippet
                or ""
            ).strip()

            snippet = snippet[
                : self.max_source_chars
            ]

            block = (
                self._source_header(
                    index,
                    result.title,
                    result.url,
                )
                + f"Snippet: {snippet}"
            )

            remaining = (
                self.max_context_chars
                - total_chars
            )

            if remaining <= 0:
                break

            block = block[:remaining]

            blocks.append(block)
            selected.append(result)

            total_chars += len(block)

        text = "\n\n".join(blocks)

        return WebContext(
            query=query,
            text=text[: self.max_context_chars],
            sources=selected,
        )

    def from_fetched_pages(
        self,
        query: str,
        pages: list[WebPageResponse],
    ) -> WebContext:

        blocks: list[str] = []
        selected_sources: list[WebSearchResult] = []

        total_chars = 0

        for index, page in enumerate(
            pages,
            start=1,
        ):
            if not page.success:
                continue

            content = (
                page.text
                or ""
            ).strip()

            if not content:
                continue

            content = content[
                : self.max_source_chars
            ]

            block = (
                self._source_header(
                    index,
                    page.title or page.final_url,
                    page.final_url,
                )
                + "Content:\n"
                + content
            )

            remaining = (
                self.max_context_chars
                - total_chars
            )

            if remaining <= 0:
                break

            block = block[:remaining]

            blocks.append(block)

            selected_sources.append(
                WebSearchResult(
                    title=page.title
                    or page.final_url,
                    url=page.final_url,
                    snippet=content[:500],
                    source="web_fetch",
                    score=page.score,
                )
            )

            total_chars += len(block)

        text = "\n\n".join(blocks)

        return WebContext(
            query=query,
            text=text[: self.max_context_chars],
            sources=selected_sources,
        )


web_context_builder = WebContextBuilder()