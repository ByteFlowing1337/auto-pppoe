import re

from .get_gateway import get_gateway_ip
import requests

gateway = get_gateway_ip()
if gateway is None:
    print("Unable to determine router IP address.")
    exit(1)


def check_router_vendor() -> str | None:
    try:
        response = requests.get(f"http://{gateway}", timeout=5)
        server_body = response.text
        match = re.search(
            r"TP-LINK|D-Link|Netgear|ASUS|Linksys|Huawei", server_body, re.IGNORECASE
        )
        if match:
            return match.group(0)
    except requests.RequestException as e:
        print(f"Error connecting to router: {e}")
        return None
