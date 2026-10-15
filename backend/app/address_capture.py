"""Capture US property addresses from a listing URL.

Uses the same HTML fetch + regex approach as the original desktop script
(address_capture_v1.58.py), then returns addresses for user review.
"""

from __future__ import annotations

import html
import ipaddress
import re
import socket
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse
from urllib.request import Request, urlopen

from app.address_patterns import STATES, STREETS

MAX_BYTES = 2_000_000
FETCH_TIMEOUT = 15
USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
)

_WORD = r"[a-zA-Z0-9]+(?:[.,])?"
_STREET_NAME = rf"(?:\s+{_WORD}){{1,4}}"
_STREETS = "|".join(re.escape(s) for s in STREETS)
_STATES = "|".join(re.escape(s) for s in STATES)

# Same shape as the original script: number + street + type + city + state + zip
ADDRESS_RE = re.compile(
    rf"\b\d+\b"
    rf"{_STREET_NAME}"
    rf"\s+(?:{_STREETS})[.,]?"
    rf"{_STREET_NAME}"
    rf"\s+(?:{_STATES})[.,]?"
    rf"\s*\d{{5}}(?:[.,]?)",
    flags=re.IGNORECASE,
)

# Original OCR fallback: zip optional
ADDRESS_RE_NO_ZIP = re.compile(
    rf"\b\d+\b"
    rf"{_STREET_NAME}"
    rf"\s+(?:{_STREETS})[.,]?"
    rf"{_STREET_NAME}"
    rf"\s+(?:{_STATES})[.,]?"
    rf"(?:\s*\d{{5}})?"
    rf"\b",
    flags=re.IGNORECASE,
)

_SCRUB = str.maketrans({'"': " ", "/": " ", "<": " ", ">": " ", "=": " "})
_SCRIPT_RE = re.compile(r"<(script|style|noscript)\b[^>]*>.*?</\1>", re.I | re.S)
_TAG_RE = re.compile(r"<[^>]+>")


class AddressCaptureError(ValueError):
    pass


def _normalize_url(raw: str) -> str:
    url = (raw or "").strip()
    if not url:
        raise AddressCaptureError("A listing URL is required")
    if not url.lower().startswith(("http://", "https://")):
        url = "https://" + url
    parsed = urlparse(url)
    if parsed.scheme not in {"http", "https"} or not parsed.hostname:
        raise AddressCaptureError("Enter a valid http or https URL")
    return url


def _assert_public_host(hostname: str) -> None:
    host = hostname.strip("[]").lower()
    if host in {"localhost", "127.0.0.1", "::1"} or host.endswith(".local"):
        raise AddressCaptureError("That URL cannot be used")
    try:
        infos = socket.getaddrinfo(host, None)
    except socket.gaierror as exc:
        raise AddressCaptureError("Could not resolve that URL") from exc
    for info in infos:
        ip = ipaddress.ip_address(info[4][0])
        if ip.is_private or ip.is_loopback or ip.is_link_local or ip.is_reserved or ip.is_multicast:
            raise AddressCaptureError("That URL cannot be used")


def _visible_text(raw_html: str) -> str:
    cleaned = _SCRIPT_RE.sub(" ", raw_html)
    cleaned = html.unescape(cleaned)
    stripped = _TAG_RE.sub(" ", cleaned)
    return " ".join(stripped.split())


def extract_addresses_from_text(text: str, include_no_zip: bool = False) -> list[str]:
    if not text:
        return []
    collapsed = " ".join(text.split())
    scrubbed = collapsed.translate(_SCRUB)
    scrubbed = re.sub(r"\s+", " ", scrubbed)
    patterns = [ADDRESS_RE]
    if include_no_zip:
        patterns.append(ADDRESS_RE_NO_ZIP)
    found: list[str] = []
    for pattern in patterns:
        found.extend(m.group(0) for m in pattern.finditer(collapsed))
        found.extend(m.group(0) for m in pattern.finditer(scrubbed))
    seen: set[str] = set()
    out: list[str] = []
    for item in found:
        normalized = re.sub(r"\s+", " ", item).strip(" .,")
        key = normalized.lower()
        if key and key not in seen:
            seen.add(key)
            out.append(normalized)
    return out


def fetch_listing_text(url: str) -> tuple[str, str]:
    target = _normalize_url(url)
    _assert_public_host(urlparse(target).hostname or "")
    request = Request(
        target,
        headers={
            "User-Agent": USER_AGENT,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        },
        method="GET",
    )
    try:
        with urlopen(request, timeout=FETCH_TIMEOUT) as response:
            final_url = response.geturl() or target
            _assert_public_host(urlparse(final_url).hostname or "")
            content_type = (response.headers.get("Content-Type") or "").lower()
            body = response.read(MAX_BYTES + 1)
    except HTTPError as exc:
        raise AddressCaptureError(f"The listing page returned HTTP {exc.code}") from exc
    except URLError as exc:
        raise AddressCaptureError("Could not open that listing URL") from exc
    except TimeoutError as exc:
        raise AddressCaptureError("The listing page took too long to respond") from exc

    if len(body) > MAX_BYTES:
        body = body[:MAX_BYTES]
    charset = "utf-8"
    if "charset=" in content_type:
        charset = content_type.split("charset=", 1)[1].split(";")[0].strip() or "utf-8"
    text = body.decode(charset, errors="ignore")
    return final_url, text


def capture_addresses_from_url(url: str) -> dict:
    final_url, raw = fetch_listing_text(url)
    visible = _visible_text(raw)
    # Match original script: scan raw HTML and the cleaned visible text.
    addresses = extract_addresses_from_text(raw) + extract_addresses_from_text(visible)
    seen: set[str] = set()
    unique: list[str] = []
    for item in addresses:
        key = item.lower()
        if key not in seen:
            seen.add(key)
            unique.append(item)
    return {"url": final_url, "addresses": unique, "count": len(unique)}
