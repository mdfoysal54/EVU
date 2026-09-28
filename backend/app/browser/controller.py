from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Optional


@dataclass
class BrowserController:
    """
    Thin adapter around a browser/page implementation.

    The wrapped object may be a Playwright Page or another
    provider-specific implementation.
    """

    page: Any = None
    timeout_ms: int = 30_000
    metadata: Dict[str, Any] = field(default_factory=dict)

    def attach(self, page: Any) -> None:
        self.page = page

    def require_page(self) -> Any:
        if self.page is None:
            raise RuntimeError(
                "No browser page is attached."
            )

        return self.page

    async def goto(
        self,
        url: str,
        wait_until: str = "domcontentloaded",
    ) -> Any:
        page = self.require_page()

        return await page.goto(
            url,
            wait_until=wait_until,
            timeout=self.timeout_ms,
        )

    async def reload(self) -> Any:
        return await self.require_page().reload(
            timeout=self.timeout_ms
        )

    async def go_back(self) -> Any:
        return await self.require_page().go_back(
            timeout=self.timeout_ms
        )

    async def go_forward(self) -> Any:
        return await self.require_page().go_forward(
            timeout=self.timeout_ms
        )

    async def wait_for_load_state(
        self,
        state: str = "domcontentloaded",
    ) -> None:
        await self.require_page().wait_for_load_state(
            state
        )

    async def title(self) -> str:
        return await self.require_page().title()

    def url(self) -> str:
        return str(
            getattr(
                self.require_page(),
                "url",
                "",
            )
        )