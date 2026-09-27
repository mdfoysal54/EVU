from __future__ import annotations

import asyncio
import uuid
from dataclasses import dataclass

from playwright.async_api import (
    Browser,
    BrowserContext,
    Page,
    Playwright,
)


@dataclass
class BrowserSession:
    session_id: str
    browser: Browser
    context: BrowserContext
    page: Page


class BrowserSessionManager:
    """
    In-memory browser session manager.

    Step 16:
        one FastAPI process

    Future:
        dedicated browser workers / Redis / remote browser service
    """

    def __init__(self):
        self._sessions: dict[
            str,
            BrowserSession,
        ] = {}

        self._lock = asyncio.Lock()

    async def create(
        self,
        playwright: Playwright,
        headless: bool = True,
    ) -> BrowserSession:

        browser = await playwright.chromium.launch(
            headless=headless,
        )

        context = await browser.new_context(
            viewport={
                "width": 1440,
                "height": 900,
            },
            ignore_https_errors=False,
        )

        page = await context.new_page()

        session_id = str(
            uuid.uuid4()
        )

        session = BrowserSession(
            session_id=session_id,
            browser=browser,
            context=context,
            page=page,
        )

        async with self._lock:
            self._sessions[
                session_id
            ] = session

        return session

    async def get(
        self,
        session_id: str,
    ) -> BrowserSession:

        async with self._lock:
            session = self._sessions.get(
                session_id
            )

        if not session:
            raise KeyError(
                f"Browser session not found: "
                f"{session_id}"
            )

        return session

    async def close(
        self,
        session_id: str,
    ) -> bool:

        async with self._lock:
            session = self._sessions.pop(
                session_id,
                None,
            )

        if not session:
            return False

        try:
            await session.context.close()
        finally:
            await session.browser.close()

        return True

    async def close_all(self):
        async with self._lock:
            sessions = list(
                self._sessions.values()
            )

            self._sessions.clear()

        for session in sessions:
            try:
                await session.context.close()
            except Exception:
                pass

            try:
                await session.browser.close()
            except Exception:
                pass


browser_session_manager = (
    BrowserSessionManager()
)