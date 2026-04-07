import logging
import re
from collections.abc import Iterator

import requests
from autodialer.apis.utils.get_gateway import format_ip_for_url_host, get_gateway_ip


logger = logging.getLogger(__name__)
TITLE_PATTERN = re.compile(r"<title\b[^>]*>(.*?)</title>", re.IGNORECASE | re.DOTALL)

VENDOR_SIGNATURES: dict[str, tuple[str, ...]] = {
    "TP-Link": ("tp-link", "tplink", "tl-", "archer", "deco", "tplinkwifi.net"),
    "Netgear": ("netgear", "orbi"),
    "D-Link": ("d-link", "dlink"),
    "ASUS": ("asus", "rt-", "asuswrt"),
    "Linksys": (
        "linksys",
        "e1200",
        "e2500",
        "e3200",
        "e4200",
        "e5400",
        "e7200",
        "e8400",
    ),
    "Xiaomi": ("xiaomi", "miwifi"),
    "Huawei": ("huawei", "e5770", "e5773", "e5776"),
    "Zyxel": ("zyxel", "zywall", "zyxel.com"),
    "TP-Link Omada": ("omada", "tp-link omada"),
    "MikroTik": ("mikrotik", "routeros"),
    "Ubiquiti": ("ubiquiti", "unifi"),
    "Netis": ("netis", "netis.com"),
    "Tenda": ("tenda", "tendawifi.com"),
    "Mercusys": ("mercusys", "mercusys.com"),
    "Edimax": ("edimax", "edimax.com"),
    "GL.iNet": ("gl.inet", "glinet.com"),
    "Buffalo": ("buffalo", "buffalotech.com"),
    "ASUS AiMesh": ("aimesh", "asus aimesh"),
    "Netgear Orbi": ("orbi", "netgear orbi"),
    "Linksys Velop": ("velop", "linksys velop"),
    "ZTE": ("zte", "zte.com.cn", "中兴"),
    "Google Nest Wifi": ("nest wifi", "google nest wifi"),
    "Eero": ("eero", "eero.com"),
}


def _match_vendor_marker(text: str) -> str | None:
    normalized_text = text.casefold()

    for vendor, markers in VENDOR_SIGNATURES.items():
        if any(marker in normalized_text for marker in markers):
            return vendor

    return None


def _extract_title(text: str) -> str:
    match = TITLE_PATTERN.search(text)
    return match.group(1) if match else ""


def _iter_response_chain(response: requests.Response) -> Iterator[requests.Response]:
    yield from getattr(response, "history", [])
    yield response


def check_router_vendor() -> str | None:
    gateway = get_gateway_ip()
    if gateway is None:
        logger.error("Unable to determine router IP address.")
        return None

    try:
        gateway_host = format_ip_for_url_host(gateway)
        response = requests.get(f"http://{gateway_host}", timeout=5)
        response.raise_for_status()

        title = _extract_title(response.text)
        if title:
            vendor = _match_vendor_marker(title)
            if vendor is not None:
                return vendor

        for candidate_response in _iter_response_chain(response):
            if getattr(candidate_response, "url", ""):
                vendor = _match_vendor_marker(candidate_response.url)
                if vendor is not None:
                    return vendor

            headers = getattr(candidate_response, "headers", {}) or {}
            location = headers.get("Location") or headers.get("location")
            if location:
                vendor = _match_vendor_marker(location)
                if vendor is not None:
                    return vendor

            header_text = " ".join(
                f"{name}: {value}" for name, value in headers.items()
            )
            if header_text:
                vendor = _match_vendor_marker(header_text)
                if vendor is not None:
                    return vendor

        vendor = _match_vendor_marker(response.text)
        if vendor is not None:
            return vendor

        logger.error("Unknown router vendor.")
        return None
    except requests.RequestException as e:
        logger.error("Error connecting to router: %s", e)
        return None


if __name__ == "__main__":
    vendor = check_router_vendor()
    if vendor:
        print(f"Detected router vendor: {vendor}")
    else:
        print("Router vendor could not be determined.")
