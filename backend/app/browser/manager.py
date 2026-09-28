from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Optional
import uuid


@dataclass
class BrowserSession:
    session_id: str = field(
        default_factory=lambda: str(uuid.uuid4())
    )
    browser_type: str = "chromium"
    headless: bool = True
    current_url: Optional[str] = None
    active: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)


class BrowserManager:
    """
    Provider-neutral browser session manager.

    A real browser adapter such as Playwright can be attached later
    through launch_callback / close_callback.
    """

    def __init__(
        self,
        launch_callback=None,
        close_callback=None,
    ) -> None:
        self.launch_callback = launch_callback
        self.close_callback = close_callback

        self._sessions: Dict[str, BrowserSession] = {}
        self._handles: Dict[str, Any] = {}

    def create_session(
        self,
        browser_type: str = "chromium",
        headless: bool = True,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> BrowserSession:
        session = BrowserSession(
            browser_type=browser_type,
            headless=headless,
            metadata=dict(metadata or {}),
        )

        self._sessions[session.session_id] = session

        return session

    async def launch(
        self,
        session_id: str,
    ) -> BrowserSession:
        session = self._require(session_id)

        if session.active:
            return session

        if self.launch_callback is not None:
            handle = await self.launch_callback(session)
            self._handles[session_id] = handle

        session.active = True

        return session

    async def close(
        self,
        session_id: str,
    ) -> None:
        session = self._require(session_id)

        handle = self._handles.pop(
            session_id,
            None,
        )

        if self.close_callback is not None:
            await self.close_callback(
                session,
                handle,
            )

        session.active = False

    def get(
        self,
        session_id: str,
    ) -> Optional[BrowserSession]:
        return self._sessions.get(session_id)

    def handle(
        self,
        session_id: str,
    ) -> Any:
        return self._handles.get(session_id)

    def list_sessions(self) -> list[BrowserSession]:
        return list(self._sessions.values())

    async def close_all(self) -> None:
        for session_id in list(self._sessions):
            session = self._sessions[session_id]

            if session.active:
                await self.close(session_id)

    def remove(
        self,
        session_id: str,
    ) -> bool:
        self._handles.pop(session_id, None)
        return (
            self._sessions.pop(
                session_id,
                None,
            )
            is not None
        )

    def _require(
        self,
        session_id: str,
    ) -> BrowserSession:
        session = self.get(session_id)

        if session is None:
            raise KeyError(
                f"Browser session not found: {session_id}"
            )

        return session