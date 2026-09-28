from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterable, Set
from urllib.parse import urlparse


@dataclass
class BrowserPolicy:
    allowed_domains: Set[str] = field(
        default_factory=set
    )

    allow_downloads: bool = True
    allow_screenshots: bool = True

    allow_external_navigation: bool = False

    blocked_schemes: Set[str] = field(
        default_factory=lambda: {
            "file",
            "javascript",
            "data",
        }
    )

    def validate_url(
        self,
        url: str,
    ) -> None:
        parsed = urlparse(url)

        if parsed.scheme.lower() in self.blocked_schemes:
            raise PermissionError(
                f"URL scheme blocked: {parsed.scheme}"
            )

        if (
            parsed.scheme not in {
                "http",
                "https",
            }
        ):
            raise PermissionError(
                f"Unsupported browser URL: {url}"
            )

        if self.allowed_domains:
            hostname = (
                parsed.hostname or ""
            ).lower()

            allowed = any(
                hostname == domain
                or hostname.endswith("." + domain)
                for domain in self.allowed_domains
            )

            if not allowed:
                raise PermissionError(
                    f"Domain not allowed: {hostname}"
                )

    def check_downloads(self) -> None:
        if not self.allow_downloads:
            raise PermissionError(
                "Downloads are disabled by browser policy."
            )

    def check_screenshot(self) -> None:
        if not self.allow_screenshots:
            raise PermissionError(
                "Screenshots are disabled by browser policy."
            )