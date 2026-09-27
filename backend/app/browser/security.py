from __future__ import annotations

import ipaddress
import socket
from urllib.parse import urlparse


class BrowserSecurityError(RuntimeError):
    pass


ALLOWED_SCHEMES = {
    "http",
    "https",
}


def validate_browser_url(url: str) -> str:
    if not url:
        raise BrowserSecurityError(
            "Browser URL is required."
        )

    url = url.strip()

    if len(url) > 2048:
        raise BrowserSecurityError(
            "Browser URL is too long."
        )

    parsed = urlparse(url)

    if parsed.scheme.lower() not in ALLOWED_SCHEMES:
        raise BrowserSecurityError(
            "Only HTTP and HTTPS URLs are allowed."
        )

    hostname = parsed.hostname

    if not hostname:
        raise BrowserSecurityError(
            "Browser URL has no hostname."
        )

    hostname = hostname.lower().strip()

    blocked_hostnames = {
        "localhost",
        "localhost.localdomain",
        "ip6-localhost",
    }

    if hostname in blocked_hostnames:
        raise BrowserSecurityError(
            "Localhost access is blocked."
        )

    if hostname.endswith(".local"):
        raise BrowserSecurityError(
            "Local network hostnames are blocked."
        )

    try:
        addresses = socket.getaddrinfo(
            hostname,
            None,
            type=socket.SOCK_STREAM,
        )
    except socket.gaierror as exc:
        raise BrowserSecurityError(
            f"Unable to resolve browser host: {hostname}"
        ) from exc

    unique_addresses = {
        item[4][0]
        for item in addresses
        if item and item[4]
    }

    for address in unique_addresses:
        try:
            ip = ipaddress.ip_address(
                address
            )
        except ValueError:
            continue

        if any(
            [
                ip.is_private,
                ip.is_loopback,
                ip.is_link_local,
                ip.is_reserved,
                ip.is_multicast,
                ip.is_unspecified,
            ]
        ):
            raise BrowserSecurityError(
                "Private, local, reserved, or "
                "link-local addresses are blocked."
            )

    return url


def validate_navigation_url(url: str) -> str:
    return validate_browser_url(url)