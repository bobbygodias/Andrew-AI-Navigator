from __future__ import annotations

import ipaddress
import socket
from dataclasses import dataclass
from urllib.parse import urlsplit


class UnsafeTarget(ValueError):
    pass


@dataclass(frozen=True, slots=True)
class ResolvedTarget:
    url: str
    hostname: str
    addresses: tuple[str, ...]


def _is_forbidden_ip(value: str) -> bool:
    ip = ipaddress.ip_address(value)
    return (
        ip.is_private
        or ip.is_loopback
        or ip.is_link_local
        or ip.is_multicast
        or ip.is_unspecified
        or ip.is_reserved
    )


def resolve_public_http_target(url: str) -> ResolvedTarget:
    parsed = urlsplit(url)
    if parsed.scheme.lower() not in {"http", "https"}:
        raise UnsafeTarget("only http and https targets are allowed")
    if not parsed.hostname:
        raise UnsafeTarget("target has no hostname")
    if parsed.username or parsed.password:
        raise UnsafeTarget("credentials in URLs are not allowed")

    hostname = parsed.hostname.rstrip(".")

    try:
        literal = ipaddress.ip_address(hostname)
    except ValueError:
        literal = None

    if literal is not None:
        if _is_forbidden_ip(str(literal)):
            raise UnsafeTarget("target resolves to a protected address")
        return ResolvedTarget(url=url, hostname=hostname, addresses=(str(literal),))

    try:
        infos = socket.getaddrinfo(hostname, parsed.port or 443, type=socket.SOCK_STREAM)
    except socket.gaierror as exc:
        raise UnsafeTarget(f"hostname resolution failed: {hostname}") from exc

    addresses = tuple(sorted({item[4][0] for item in infos}))
    if not addresses:
        raise UnsafeTarget("hostname resolved to no addresses")
    if any(_is_forbidden_ip(address) for address in addresses):
        raise UnsafeTarget("target resolves to a protected address")

    return ResolvedTarget(url=url, hostname=hostname, addresses=addresses)
