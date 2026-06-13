from __future__ import annotations

import ipaddress
import socket
from urllib.parse import urlparse

from fastapi import HTTPException, status

from app.core.config import settings


def validate_public_url(url: str) -> str:
    parsed = urlparse(url)
    if parsed.scheme.lower() not in settings.allowed_schemes:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="URL scheme is not allowed")
    if not parsed.netloc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="URL host is required")

    host = parsed.hostname
    if not host:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="URL host is invalid")

    # Basic SSRF protection. Production systems should also use DNS pinning, async resolution,
    # egress firewalling, malware scanning, and blocklists.
    try:
        addresses = socket.getaddrinfo(host, None)
    except socket.gaierror as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="URL host cannot be resolved") from exc

    for address in addresses:
        ip = ipaddress.ip_address(address[4][0])
        if ip.is_private or ip.is_loopback or ip.is_link_local or ip.is_multicast or ip.is_reserved:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="URL host is not allowed")

    return url
