import requests
from .get_gateway import get_gateway_ip

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
    "ZTE": ("zte", "zte.com.cn"),
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
    "Google Nest Wifi": ("nest wifi", "google nest wifi"),
    "Eero": ("eero", "eero.com"),
}


def check_router_vendor() -> str | None:
    gateway = get_gateway_ip()
    if gateway is None:
        print("Unable to determine router IP address.")
        return None

    try:
        response = requests.get(f"http://{gateway}", timeout=5)
        response.raise_for_status()

        body = (response.text or "")[:20000].casefold()
        server = response.headers.get("Server", "").casefold()
        location = response.headers.get("Location", "").casefold()
        fingerprint = " ".join((body, server, location))

        for vendor, markers in VENDOR_SIGNATURES.items():
            if any(marker in fingerprint for marker in markers):
                return vendor

        print("Unknown router vendor.")
        return None
    except requests.RequestException as e:
        print(f"Error connecting to router: {e}")
        return None
