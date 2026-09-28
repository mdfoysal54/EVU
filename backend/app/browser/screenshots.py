from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Optional


@dataclass
class ScreenshotResult:
    path: str
    full_page: bool = False


class ScreenshotManager:
    def __init__(self, page: Any = None) -> None:
        self.page = page

    def attach(self, page: Any) -> None:
        self.page = page

    async def capture(
        self,
        path: str,
        full_page: bool = True,
    ) -> ScreenshotResult:
        if self.page is None:
            raise RuntimeError(
                "No browser page is attached."
            )

        output = Path(path)

        output.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        await self.page.screenshot(
            path=str(output),
            full_page=full_page,
        )

        return ScreenshotResult(
            path=str(output),
            full_page=full_page,
        )

    async def capture_bytes(
        self,
        full_page: bool = True,
    ) -> bytes:
        if self.page is None:
            raise RuntimeError(
                "No browser page is attached."
            )

        return await self.page.screenshot(
            full_page=full_page
        )