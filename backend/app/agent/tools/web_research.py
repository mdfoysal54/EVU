from __future__ import annotations

from app.agent.tools.base import ToolExecution
from app.core.config import settings
from app.web.research import (
    web_research_service,
)


class WebResearchTool:
    """
    EVU Agent tool for Internet research.

    The tool performs:

        search
        -> rank
        -> fetch
        -> extract
        -> context building
    """

    name = "web_research"

    async def run(
        self,
        query: str,
        max_results: int = 5,
        fetch_pages: int = 3,
    ) -> ToolExecution:

        if not settings.WEB_SEARCH_ENABLED:
            return ToolExecution(
                name=self.name,
                input=query,
                output=(
                    "Web research is disabled by "
                    "server configuration."
                ),
                success=False,
            )

        query = query.strip()

        if not query:
            return ToolExecution(
                name=self.name,
                input=query,
                output="Web research query is empty.",
                success=False,
            )

        if len(query) > 1000:
            return ToolExecution(
                name=self.name,
                input=query[:1000],
                output=(
                    "Web research query exceeds "
                    "the 1000-character limit."
                ),
                success=False,
            )

        try:
            research = (
                await web_research_service.research(
                    query=query,
                    max_results=max_results,
                    fetch_pages=fetch_pages,
                )
            )

            output_parts: list[str] = []

            output_parts.append(
                f"WEB RESEARCH QUERY: {research.query}"
            )

            output_parts.append(
                f"SEARCH PROVIDER: {research.provider}"
            )

            if research.search_results:
                output_parts.append(
                    "\nSEARCH SOURCES:"
                )

                for index, result in enumerate(
                    research.search_results,
                    start=1,
                ):
                    output_parts.append(
                        (
                            f"[{index}] "
                            f"{result.title}\n"
                            f"URL: {result.url}\n"
                            f"Score: {result.score:.4f}\n"
                            f"Snippet: {result.snippet}"
                        )
                    )

            if research.pages:
                output_parts.append(
                    "\nFETCHED SOURCES:"
                )

                for index, page in enumerate(
                    research.pages,
                    start=1,
                ):
                    if page.success:
                        output_parts.append(
                            (
                                f"[{index}] "
                                f"{page.title}\n"
                                f"URL: {page.final_url}\n"
                                f"Status: "
                                f"{page.status_code}\n"
                                f"Content:\n"
                                f"{page.text[:3000]}"
                            )
                        )
                    else:
                        output_parts.append(
                            (
                                f"[{index}] "
                                f"{page.url}\n"
                                f"Fetch failed: "
                                f"{page.error}"
                            )
                        )

            if research.context.text:
                output_parts.append(
                    "\nRESEARCH CONTEXT:"
                )
                output_parts.append(
                    research.context.text
                )
            else:
                output_parts.append(
                    "\nRESEARCH CONTEXT:\n"
                    "No usable web content was extracted."
                )

            output = "\n\n".join(
                output_parts
            )

            # Final hard bound before the agent
            # receives the result.
            output = output[
                : settings.AGENT_MAX_TOOL_OUTPUT_CHARS
            ]

            return ToolExecution(
                name=self.name,
                input=query,
                output=output,
                success=True,
            )

        except Exception as exc:
            return ToolExecution(
                name=self.name,
                input=query,
                output=(
                    f"Web research failed: {exc}"
                ),
                success=False,
            )


web_research_tool = WebResearchTool()