from __future__ import annotations

import base64
from typing import Any

from playwright.async_api import (
    TimeoutError as PlaywrightTimeoutError,
    async_playwright,
)

from app.browser.schemas import (
    BrowserActionResponse,
    BrowserInspectResponse,
    BrowserOpenResponse,
    BrowserScreenshotResponse,
)
from app.browser.security import (
    BrowserSecurityError,
    validate_browser_url,
    validate_navigation_url,
)
from app.browser.session import (
    BrowserSession,
    browser_session_manager,
)
from app.core.config import settings


class BrowserService:
    """
    Controlled browser automation service.

    Supported operations:

    - open
    - inspect
    - click
    - fill
    - press
    - back
    - forward
    - screenshot

    The browser does NOT expose arbitrary JavaScript execution.
    """

    def __init__(self):
        self._playwright = None
        self._start_lock = None

    async def _ensure_started(self):
        if self._playwright is not None:
            return

        if self._start_lock is None:
            import asyncio

            self._start_lock = asyncio.Lock()

        async with self._start_lock:
            if self._playwright is None:
                self._playwright = (
                    await async_playwright().start()
                )

    async def shutdown(self):
        await browser_session_manager.close_all()

        if self._playwright is not None:
            await self._playwright.stop()
            self._playwright = None

    async def _get_session(
        self,
        session_id: str,
    ) -> BrowserSession:

        return await browser_session_manager.get(
            session_id
        )

    async def _snapshot(
        self,
        session: BrowserSession,
    ) -> tuple[
        str,
        str,
        str,
    ]:

        page = session.page

        title = await page.title()

        text = await page.locator(
            "body"
        ).inner_text(
            timeout=settings.BROWSER_ACTION_TIMEOUT_MS
        )

        max_chars = (
            settings.BROWSER_MAX_PAGE_TEXT_CHARS
        )

        text = text[:max_chars]

        return (
            page.url,
            title,
            text,
        )

    async def open(
        self,
        url: str,
        wait_until: str = "domcontentloaded",
    ) -> BrowserOpenResponse:

        if not settings.BROWSER_ENABLED:
            return BrowserOpenResponse(
                session_id="",
                url=url,
                title="",
                text="",
                success=False,
                error=(
                    "Browser automation is disabled."
                ),
            )

        try:
            url = validate_browser_url(url)

            await self._ensure_started()

            session = await browser_session_manager.create(
                self._playwright,
                headless=settings.BROWSER_HEADLESS,
            )

            page = session.page

            await page.goto(
                url,
                wait_until=wait_until,
                timeout=settings.BROWSER_NAVIGATION_TIMEOUT_MS,
            )

            final_url = validate_navigation_url(
                page.url
            )

            title = await page.title()

            text = await page.locator(
                "body"
            ).inner_text(
                timeout=settings.BROWSER_ACTION_TIMEOUT_MS
            )

            text = text[
                : settings.BROWSER_MAX_PAGE_TEXT_CHARS
            ]

            return BrowserOpenResponse(
                session_id=session.session_id,
                url=final_url,
                title=title,
                text=text,
                success=True,
            )

        except BrowserSecurityError as exc:
            return BrowserOpenResponse(
                session_id="",
                url=url,
                title="",
                text="",
                success=False,
                error=str(exc),
            )

        except PlaywrightTimeoutError:
            return BrowserOpenResponse(
                session_id="",
                url=url,
                title="",
                text="",
                success=False,
                error="Browser navigation timed out.",
            )

        except Exception as exc:
            return BrowserOpenResponse(
                session_id="",
                url=url,
                title="",
                text="",
                success=False,
                error=f"Browser open failed: {exc}",
            )

    async def inspect(
        self,
        session_id: str,
    ) -> BrowserInspectResponse:

        try:
            session = await self._get_session(
                session_id
            )

            url, title, text = (
                await self._snapshot(session)
            )

            links = await session.page.locator(
                "a"
            ).evaluate_all(
                """
                elements => elements
                    .slice(0, 100)
                    .map(a => ({
                        text: (a.innerText || '').trim(),
                        href: a.href || ''
                    }))
                    .filter(x => x.text || x.href)
                """
            )

            safe_links: list[
                dict[str, str]
            ] = []

            for link in links:
                href = str(
                    link.get("href", "")
                ).strip()

                text_value = str(
                    link.get("text", "")
                ).strip()

                if not href:
                    continue

                try:
                    validate_browser_url(
                        href
                    )
                except Exception:
                    continue

                safe_links.append(
                    {
                        "text": text_value[
                            :500
                        ],
                        "href": href,
                    }
                )

            return BrowserInspectResponse(
                session_id=session_id,
                url=url,
                title=title,
                text=text,
                links=safe_links,
                success=True,
            )

        except Exception as exc:
            return BrowserInspectResponse(
                session_id=session_id,
                url="",
                title="",
                text="",
                links=[],
                success=False,
                error=f"Inspection failed: {exc}",
            )

    async def click(
        self,
        session_id: str,
        selector: str,
        wait_after: int = 500,
    ) -> BrowserActionResponse:

        try:
            session = await self._get_session(
                session_id
            )

            locator = session.page.locator(
                selector
            ).first

            await locator.wait_for(
                state="visible",
                timeout=settings.BROWSER_ACTION_TIMEOUT_MS,
            )

            await locator.click(
                timeout=settings.BROWSER_ACTION_TIMEOUT_MS
            )

            if wait_after:
                await session.page.wait_for_timeout(
                    wait_after
                )

            url, title, text = (
                await self._snapshot(session)
            )

            return BrowserActionResponse(
                session_id=session_id,
                url=url,
                title=title,
                text=text,
                success=True,
            )

        except PlaywrightTimeoutError:
            return BrowserActionResponse(
                session_id=session_id,
                url="",
                title="",
                text="",
                success=False,
                error=(
                    "Browser click timed out."
                ),
            )

        except Exception as exc:
            return BrowserActionResponse(
                session_id=session_id,
                url="",
                title="",
                text="",
                success=False,
                error=f"Browser click failed: {exc}",
            )

    async def fill(
        self,
        session_id: str,
        selector: str,
        value: str,
        wait_after: int = 200,
    ) -> BrowserActionResponse:

        try:
            session = await self._get_session(
                session_id
            )

            locator = session.page.locator(
                selector
            ).first

            await locator.wait_for(
                state="visible",
                timeout=settings.BROWSER_ACTION_TIMEOUT_MS,
            )

            await locator.fill(
                value,
                timeout=settings.BROWSER_ACTION_TIMEOUT_MS,
            )

            if wait_after:
                await session.page.wait_for_timeout(
                    wait_after
                )

            url, title, text = (
                await self._snapshot(session)
            )

            return BrowserActionResponse(
                session_id=session_id,
                url=url,
                title=title,
                text=text,
                success=True,
            )

        except Exception as exc:
            return BrowserActionResponse(
                session_id=session_id,
                url="",
                title="",
                text="",
                success=False,
                error=f"Browser fill failed: {exc}",
            )

    async def press(
        self,
        session_id: str,
        selector: str,
        key: str,
        wait_after: int = 500,
    ) -> BrowserActionResponse:

        try:
            session = await self._get_session(
                session_id
            )

            locator = session.page.locator(
                selector
            ).first

            await locator.wait_for(
                state="visible",
                timeout=settings.BROWSER_ACTION_TIMEOUT_MS,
            )

            await locator.press(
                key,
                timeout=settings.BROWSER_ACTION_TIMEOUT_MS,
            )

            if wait_after:
                await session.page.wait_for_timeout(
                    wait_after
                )

            url, title, text = (
                await self._snapshot(session)
            )

            return BrowserActionResponse(
                session_id=session_id,
                url=url,
                title=title,
                text=text,
                success=True,
            )

        except Exception as exc:
            return BrowserActionResponse(
                session_id=session_id,
                url="",
                title="",
                text="",
                success=False,
                error=f"Browser press failed: {exc}",
            )

    async def back(
        self,
        session_id: str,
    ) -> BrowserActionResponse:

        try:
            session = await self._get_session(
                session_id
            )

            await session.page.go_back(
                wait_until="domcontentloaded",
                timeout=settings.BROWSER_NAVIGATION_TIMEOUT_MS,
            )

            url, title, text = (
                await self._snapshot(session)
            )

            return BrowserActionResponse(
                session_id=session_id,
                url=url,
                title=title,
                text=text,
                success=True,
            )

        except Exception as exc:
            return BrowserActionResponse(
                session_id=session_id,
                url="",
                title="",
                text="",
                success=False,
                error=f"Browser back failed: {exc}",
            )

    async def forward(
        self,
        session_id: str,
    ) -> BrowserActionResponse:

        try:
            session = await self._get_session(
                session_id
            )

            await session.page.go_forward(
                wait_until="domcontentloaded",
                timeout=settings.BROWSER_NAVIGATION_TIMEOUT_MS,
            )

            url, title, text = (
                await self._snapshot(session)
            )

            return BrowserActionResponse(
                session_id=session_id,
                url=url,
                title=title,
                text=text,
                success=True,
            )

        except Exception as exc:
            return BrowserActionResponse(
                session_id=session_id,
                url="",
                title="",
                text="",
                success=False,
                error=f"Browser forward failed: {exc}",
            )

    async def screenshot(
        self,
        session_id: str,
        full_page: bool = False,
    ) -> BrowserScreenshotResponse:

        try:
            session = await self._get_session(
                session_id
            )

            image = await session.page.screenshot(
                full_page=full_page,
                type="png",
            )

            encoded = base64.b64encode(
                image
            ).decode("ascii")

            return BrowserScreenshotResponse(
                session_id=session_id,
                url=session.page.url,
                title=await session.page.title(),
                image_base64=encoded,
                success=True,
            )

        except Exception as exc:
            return BrowserScreenshotResponse(
                session_id=session_id,
                url="",
                title="",
                image_base64="",
                success=False,
                error=(
                    f"Browser screenshot failed: "
                    f"{exc}"
                ),
            )

    async def close(
        self,
        session_id: str,
    ) -> bool:

        return await browser_session_manager.close(
            session_id
        )


browser_service = BrowserService()