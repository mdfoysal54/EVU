from __future__ import annotations

from urllib.parse import urljoin, urlparse
from typing import Iterable, Optional


class NavigationManager:
    def __init__(
        self,
        allowed_domains: Optional[Iterable[str]] = None,
    ) -> None:
        self.allowed_domains = {
            domain.lower()
            for domain in (allowed_domains or [])
        }

    def resolve(
        self,
        base_url: str,
        target: str,
    ) -> str:
        return urljoin(base_url, target)

    def is_allowed(
        self,
        url: str,
    ) -> bool:
        if not self.allowed_domains:
            return True

        hostname = urlparse(url).hostname

        if not hostname:
            return False

        hostname = hostname.lower()

        return any(
            hostname == domain
            or hostname.endswith("." + domain)
            for domain in self.allowed_domains
        )

    def validate(
        self,
        url: str,
    ) -> str:
        parsed = urlparse(url)

        if parsed.scheme not in {
            "http",
            "https",
        }:
            raise ValueError(
                f"Unsupported URL scheme: {parsed.scheme}"
            )

        if not self.is_allowed(url):
            raise PermissionError(
                f"Navigation blocked by domain policy: {url}"
            )

        return url