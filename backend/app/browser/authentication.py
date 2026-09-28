from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Optional


@dataclass
class AuthenticationState:
    authenticated: bool = False
    user: Optional[str] = None
    storage_state_path: Optional[str] = None
    metadata: Dict[str, Any] = field(
        default_factory=dict
    )


class BrowserAuthenticator:
    """
    Authentication helper.

    Credentials should never be hard-coded into this class.
    Callers should provide secrets through secure configuration,
    environment variables, or a secrets manager.
    """

    def __init__(
        self,
        page: Any = None,
    ) -> None:
        self.page = page
        self.state = AuthenticationState()

    def attach(self, page: Any) -> None:
        self.page = page

    async def login(
        self,
        login_url: str,
        username_selector: str,
        password_selector: str,
        submit_selector: str,
        username: str,
        password: str,
    ) -> AuthenticationState:
        if self.page is None:
            raise RuntimeError(
                "No browser page is attached."
            )

        await self.page.goto(login_url)

        await self.page.locator(
            username_selector
        ).fill(username)

        await self.page.locator(
            password_selector
        ).fill(password)

        await self.page.locator(
            submit_selector
        ).click()

        self.state.authenticated = True
        self.state.user = username

        return self.state

    def mark_authenticated(
        self,
        user: Optional[str] = None,
    ) -> None:
        self.state.authenticated = True
        self.state.user = user

    def logout(self) -> None:
        self.state = AuthenticationState()