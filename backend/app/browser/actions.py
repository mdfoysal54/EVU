from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Optional


@dataclass
class BrowserAction:
    action: str
    selector: Optional[str] = None
    value: Optional[str] = None
    url: Optional[str] = None
    metadata: Dict[str, Any] = field(
        default_factory=dict
    )


class BrowserActions:
    def __init__(
        self,
        page: Any = None,
        timeout_ms: int = 30_000,
    ) -> None:
        self.page = page
        self.timeout_ms = timeout_ms

    def attach(self, page: Any) -> None:
        self.page = page

    def require_page(self) -> Any:
        if self.page is None:
            raise RuntimeError(
                "No browser page is attached."
            )

        return self.page

    async def click(
        self,
        selector: str,
    ) -> None:
        await self.require_page().locator(
            selector
        ).click(
            timeout=self.timeout_ms
        )

    async def fill(
        self,
        selector: str,
        value: str,
    ) -> None:
        await self.require_page().locator(
            selector
        ).fill(
            value,
            timeout=self.timeout_ms,
        )

    async def press(
        self,
        selector: str,
        key: str,
    ) -> None:
        await self.require_page().locator(
            selector
        ).press(
            key,
            timeout=self.timeout_ms,
        )

    async def select_option(
        self,
        selector: str,
        value: str,
    ) -> None:
        await self.require_page().locator(
            selector
        ).select_option(
            value,
            timeout=self.timeout_ms,
        )

    async def check(
        self,
        selector: str,
    ) -> None:
        await self.require_page().locator(
            selector
        ).check(
            timeout=self.timeout_ms
        )

    async def uncheck(
        self,
        selector: str,
    ) -> None:
        await self.require_page().locator(
            selector
        ).uncheck(
            timeout=self.timeout_ms
        )

    async def hover(
        self,
        selector: str,
    ) -> None:
        await self.require_page().locator(
            selector
        ).hover(
            timeout=self.timeout_ms
        )

    async def get_text(
        self,
        selector: str,
    ) -> str:
        return await self.require_page().locator(
            selector
        ).inner_text(
            timeout=self.timeout_ms
        )

    async def get_attribute(
        self,
        selector: str,
        attribute: str,
    ) -> Optional[str]:
        return await self.require_page().locator(
            selector
        ).get_attribute(attribute)