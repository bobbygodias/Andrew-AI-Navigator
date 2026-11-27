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
    if '%' in value:
        return True  # Scoped addresses are not public Internet destinations.
    try:
        ip = ipaddress.ip_address(value)
    except ValueError:
        return True
    if isinstance(ip, ipaddress.IPv6Address) and ip.ipv4_mapped is not None:
        ip = ip.ipv4_mapped
    return (
        not ip.is_global
        or ip.is_multicast
        or ip.is_reserved
        or ip.is_loopback
        or ip.is_link_local
        or ip.is_unspecified
    )


def resolve_public_http_target(url: str) -> ResolvedTarget:
    if not isinstance(url, str) or any(ord(c) <= 32 or ord(c) == 127 or c == '\\' for c in url):
        raise UnsafeTarget('malformed target URL')
    try:
        parsed = urlsplit(url)
        scheme = parsed.scheme.lower()
        hostname = (parsed.hostname or '').rstrip('.')
        port = parsed.port
        if scheme not in {'http', 'https'}:
            raise UnsafeTarget('only http and https targets are allowed')
        if not hostname or port == 0:
            raise UnsafeTarget('target has no hostname or has an invalid port')
        if parsed.username is not None or parsed.password is not None:
            raise UnsafeTarget('credentials in URLs are not allowed')
    except UnsafeTarget:
        raise
    except ValueError as exc:
        raise UnsafeTarget('malformed target URL') from exc

    if '%' in hostname:
        raise UnsafeTarget('scoped or encoded hostnames are not allowed')
    if port is None:
        port = 80 if scheme == 'http' else 443
    try:
        literal = ipaddress.ip_address(hostname)
    except ValueError:
        literal = None

    if literal is not None:
        if _is_forbidden_ip(str(literal)):
            raise UnsafeTarget('target resolves to a protected address')
        return ResolvedTarget(url=url, hostname=hostname, addresses=(str(literal),))

    try:
        infos = socket.getaddrinfo(hostname, port, type=socket.SOCK_STREAM)
    except (OSError, UnicodeError) as exc:
        raise UnsafeTarget('hostname resolution failed') from exc

    addresses = tuple(sorted({item[4][0] for item in infos}))
    if not addresses:
        raise UnsafeTarget('hostname resolved to no addresses')
    if any(_is_forbidden_ip(address) for address in addresses):
        raise UnsafeTarget('target resolves to a protected address')

    return ResolvedTarget(url=url, hostname=hostname, addresses=addresses)
