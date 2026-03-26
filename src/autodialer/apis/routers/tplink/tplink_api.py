import requests
from autodialer import encode

from autodialer.apis.get_gateway import get_gateway_ip
from time import sleep
from typing import Literal
from urllib.parse import unquote

from autodialer.config.config import PANEL_PASSWORD, PPPOE_USERNAME, PPPOE_PASSWORD


"""
    The payload below is based on TP-Link,it may not works on other brands of routers.
    If so, you need to replace the payload.
"""


class TPLinkAPI:
    """A class to interact with TP-Link routers using their API.

    Attributes:

        router_ip: The IP address of the router, obtained from the default gateway,
        using get_gateway_ip().

        password: The **encoded** password for logging into the router.

        username: The PPPoE username for authentication.

        pppoe_password: The PPPoE password for authentication.

        stok: The session token obtained after logging into the router, used for authenticated requests.
    """

    router_ip: str
    password: str
    username: str
    pppoe_password: str
    stok: str | None = None

    def __init__(self):
        router_ip = get_gateway_ip()
        if router_ip is None:
            print("Could not determine router IP address.")
            exit(1)

        if PANEL_PASSWORD is None:
            print("Missing required environment variable: PANEL_PASSWORD")
            exit(1)

        panel_password: str = PANEL_PASSWORD

        self.router_ip = router_ip
        self.session = requests.Session()
        self.password = encode.tplink_security_encode(panel_password)
        self.username = PPPOE_USERNAME or ""
        self.pppoe_password = PPPOE_PASSWORD or ""
        self.stok = self.__login_router()

    def __post(self, payload) -> dict:
        url = f"http://{self.router_ip}"
        response = self.session.post(url, json=payload)
        return response.json()

    def __request(self, payload) -> dict:
        url = f"http://{self.router_ip}/stok={self.stok}/ds"
        response = self.session.post(url, json=payload)
        return response.json()

    def __login_router(self) -> str | None:
        payload = {"method": "do", "login": {"password": self.password}}
        response = self.__post(payload)
        if response.get("error_code") == 0 and response.get("stok") is not None:
            print("Login successful.")
            return response.get("stok")
        else:
            print("Login failed.")
            print(response)
            exit(1)
        return None

    def set_credentials(self) -> bool:
        if not self.username or not self.pppoe_password:
            print(
                "Missing PPPoE credentials. Set PPPOE_USERNAME and PPPOE_PASSWORD for PPPoE reconnection."
            )
            return False

        payload = {
            "protocol": {
                "wan": {"wan_type": "pppoe"},
                "pppoe": {"username": self.username, "password": self.pppoe_password},
            },
            "method": "set",
        }

        response = self.__request(payload)
        if response.get("error_code") == 0:
            print("PPPoE credentials set successfully.")
            return True
        else:
            print("Failed to set PPPoE credentials.")
            print(response)
            return False

    def tplink_change_wan_status_request(
        self, action: Literal["connect", "disconnect", "renew"], method: str, proto: str
    ) -> None:
        payload = {
            "network": {"change_wan_status": {"proto": proto, "operate": action}},
            "method": method,
        }
        response = self.__request(payload)
        if response.get("error_code") == 0:
            print(f"{proto} {action} successful.")
        else:
            print(f"Failed to {action} {proto}.")
            print(response)

    def tplink_get_wan_status(self) -> dict:
        payload = {
            "network": {"name": ["wan_status", "wanv6_status"]},
            "protocol": {"name": ["dhcp", "ipv6_info"]},
            "method": "get",
        }
        response = self.__request(payload)
        if response.get("error_code") == 0:
            return response
        else:
            print("Failed to get WAN status.")
            print(response)
            return {}

    def make_pppoe_reconnection(self) -> bool:
        if not self.set_credentials():
            return False

        self.tplink_change_wan_status_request(
            action="disconnect", method="do", proto="pppoe"
        )
        # Wait for a time to make sure DHCP has assigned a new IP address
        sleep(30)
        self.tplink_change_wan_status_request(
            action="connect", method="do", proto="pppoe"
        )
        return True

    def get_connected_devices(self) -> list:
        payload = {
            "hosts_info": {"table": "host_info", "name": "cap_host_num"},
            "network": {"name": "iface_mac"},
            "hyfi": {"table": ["connected_ext"]},
            "method": "get",
        }
        response = self.__request(payload)
        if response.get("error_code") != 0:
            return []

        raw_hosts = response.get("hosts_info", {}).get("host_info", [])
        devices: list[dict] = []

        for item in raw_hosts:
            host: dict[str, str] = next(
                iter(item.values()), {}
            )  # host_info_0 / host_info_1 -> {...}
            devices.append(
                {
                    "hostname": unquote(host.get("hostname", "")) or "(unknown)",
                    "ip": host.get("ip", "-"),
                    "mac": host.get("mac", "-"),
                    "type": "wireless" if host.get("type") == "1" else "wired",
                    "is_current": host.get("is_cur_host") == "1",
                    "up_kbps": int(host.get("up_speed", "0")),
                    "down_kbps": int(host.get("down_speed", "0")),
                }
            )
        return devices

    def dhcp_renew(self) -> None:
        self.tplink_change_wan_status_request(action="renew", method="do", proto="dhcp")
