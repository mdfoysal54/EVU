from __future__ import annotations

import asyncio
import ipaddress
import socket
from dataclasses import dataclass
from urllib.parse import urlparse
from urllib.request import Request, urlopen


@dataclass
class WebPage:
    url: str
    final_url: str
    status_code: int
    content_type: str
    content: str
    content_length: int


class WebFetchError(RuntimeError):
    """Raised when EVU cannot safely or successfully fetch a web page."""


class WebFetcher:
    """
    Safe, bounded HTTP/HTTPS page fetcher for EVU.

    This is intentionally not a browser.

    It handles normal HTTP pages and does not execute JavaScript,
    render browser pages, click buttons, or interact with websites.
    """

    USER_AGENT = (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 "
        "(KHTML, like Gecko) "
        "EVU/1.0 Web Intelligence"
    )

    ALLOWED_SCHEMES = {"http", "https"}

    def __init__(
        self,
        timeout_seconds: int = 15,
        max_bytes: int = 2_000_000,
    ):
        self.timeout_seconds = timeout_seconds
        self.max_bytes = max_bytes

    # ------------------------------------------------------------------
    # URL validation
    # ------------------------------------------------------------------

    @staticmethod
    def validate_url(url: str) -> str:
        if not url:
            raise WebFetchError("URL is required.")

        url = url.strip()

        if len(url) > 2048:
            raise WebFetchError("URL is too long.")

        parsed = urlparse(url)

        if parsed.scheme.lower() not in WebFetcher.ALLOWED_SCHEMES:
            raise WebFetchError(
                "Only HTTP and HTTPS URLs are supported."
            )

        if not parsed.hostname:
            raise WebFetchError("URL hostname is missing.")

        hostname = parsed.hostname.strip().lower()

        if hostname in {
            "localhost",
            "localhost.localdomain",
        }:
            raise WebFetchError(
                "Localhost URLs are not allowed."
            )

        if hostname.endswith(".local"):
            raise WebFetchError(
                "Local network hostnames are not allowed."
            )

        return url

    # ------------------------------------------------------------------
    # SSRF protection
    # ------------------------------------------------------------------

    @staticmethod
    def _is_private_ip(address: str) -> bool:
        try:
            ip = ipaddress.ip_address(address)
        except ValueError:
            return False

        return any(
            [
                ip.is_private,
                ip.is_loopback,
                ip.is_link_local,
                ip.is_reserved,
                ip.is_multicast,
                ip.is_unspecified,
            ]
        )

    @classmethod
    def _validate_hostname_resolution(cls, hostname: str) -> None:
        """
        Prevent obvious SSRF targets such as:

        localhost
        127.0.0.1
        10.x.x.x
        172.16.x.x
        192.168.x.x
        ::1
        link-local addresses
        """

        try:
            addresses = socket.getaddrinfo(
                hostname,
                None,
                type=socket.SOCK_STREAM,
            )
        except socket.gaierror as exc:
            raise WebFetchError(
                f"Unable to resolve host: {hostname}"
            ) from exc

        unique_addresses = {
            item[4][0]
            for item in addresses
            if item and item[4]
        }

        for address in unique_addresses:
            if cls._is_private_ip(address):
                raise WebFetchError(
                    "Fetching private or local network addresses "
                    "is not allowed."
                )

    # ------------------------------------------------------------------
    # Synchronous fetch
    # ------------------------------------------------------------------

    def _fetch_sync(self, url: str) -> WebPage:
        url = self.validate_url(url)

        parsed = urlparse(url)
        hostname = parsed.hostname

        if not hostname:
            raise WebFetchError("URL hostname is missing.")

        self._validate_hostname_resolution(hostname)

        request = Request(
            url,
            headers={
                "User-Agent": self.USER_AGENT,
                "Accept": (
                    "text/html,"
                    "application/xhtml+xml,"
                    "text/plain,"
                    "application/json;q=0.9,"
                    "*/*;q=0.1"
                ),
            },
            method="GET",
        )

        try:
            with urlopen(
                request,
                timeout=self.timeout_seconds,
            ) as response:

                status_code = getattr(
                    response,
                    "status",
                    200,
                )

                final_url = response.geturl()

                content_type = (
                    response.headers.get(
                        "Content-Type",
                        "",
                    )
                    .split(";")[0]
                    .strip()
                    .lower()
                )

                # Check declared Content-Length first.
                declared_length = response.headers.get(
                    "Content-Length"
                )

                if declared_length:
                    try:
                        declared_length_int = int(
                            declared_length
                        )
                    except ValueError:
                        declared_length_int = 0

                    if declared_length_int > self.max_bytes:
                        raise WebFetchError(
                            "Remote page is larger than the "
                            "configured maximum size."
                        )

                chunks: list[bytes] = []
                total = 0

                while True:
                    chunk = response.read(64 * 1024)

                    if not chunk:
                        break

                    total += len(chunk)

                    if total > self.max_bytes:
                        raise WebFetchError(
                            "Downloaded page exceeds the "
                            "configured maximum size."
                        )

                    chunks.append(chunk)

                raw_content = b"".join(chunks)

                charset = response.headers.get_content_charset()

                if not charset:
                    charset = "utf-8"

                try:
                    text = raw_content.decode(
                        charset,
                        errors="replace",
                    )
                except LookupError:
                    text = raw_content.decode(
                        "utf-8",
                        errors="replace",
                    )

                return WebPage(
                    url=url,
                    final_url=final_url,
                    status_code=status_code,
                    content_type=content_type,
                    content=text,
                    content_length=len(raw_content),
                )

        except WebFetchError:
            raise

        except TimeoutError as exc:
            raise WebFetchError(
                "Web request timed out."
            ) from exc

        except Exception as exc:
            raise WebFetchError(
                f"Web request failed: {exc}"
            ) from exc

    # ------------------------------------------------------------------
    # Async public interface
    # ------------------------------------------------------------------

    async def fetch(self, url: str) -> WebPage:
        return await asyncio.to_thread(
            self._fetch_sync,
            url,
        )


web_fetcher = WebFetcher()