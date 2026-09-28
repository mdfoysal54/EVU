from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class ExtractedContent:
    text: str = ""
    title: str = ""
    links: List[Dict[str, str]] = field(
        default_factory=list
    )
    metadata: Dict[str, Any] = field(
        default_factory=dict
    )


class BrowserExtractor:
    def __init__(self, page: Any = None) -> None:
        self.page = page

    def attach(self, page: Any) -> None:
        self.page = page

    async def text(
        self,
        selector: str = "body",
    ) -> str:
        if self.page is None:
            raise RuntimeError(
                "No browser page is attached."
            )

        return await self.page.locator(
            selector
        ).inner_text()

    async def html(
        self,
        selector: str = "body",
    ) -> str:
        if self.page is None:
            raise RuntimeError(
                "No browser page is attached."
            )

        return await self.page.locator(
            selector
        ).inner_html()

    async def links(
        self,
    ) -> list[Dict[str, str]]:
        if self.page is None:
            raise RuntimeError(
                "No browser page is attached."
            )

        locator = self.page.locator("a")

        count = await locator.count()

        results: list[Dict[str, str]] = []

        for index in range(count):
            link = locator.nth(index)

            try:
                text = (
                    await link.inner_text()
                ).strip()
            except Exception:
                text = ""

            href = await link.get_attribute(
                "href"
            )

            if href:
                results.append(
                    {
                        "text": text,
                        "href": href,
                    }
                )

        return results

    async def extract(
        self,
        selector: str = "body",
    ) -> ExtractedContent:
        if self.page is None:
            raise RuntimeError(
                "No browser page is attached."
            )

        title = await self.page.title()

        return ExtractedContent(
            text=await self.text(selector),
            title=title,
            links=await self.links(),
        )