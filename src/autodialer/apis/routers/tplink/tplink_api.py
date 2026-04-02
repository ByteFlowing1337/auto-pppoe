import logging
import requests
from autodialer import encode

from autodialer.apis.utils.get_gateway import format_ip_for_url_host, get_gateway_ip
from time import sleep
from typing import Literal
from urllib.parse import unquote
from autodialer.config.config import PANEL_PASSWORD, PPPOE_USERNAME, PPPOE_PASSWORD

logger = logging.getLogger(__name__)

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

    SUPPORTED_VENDORS = ("TP-Link",)

    router_ip: str
    password: str
    username: str
    pppoe_password: str
    stok: str | None = None

    def __init__(self):
        router_ip = get_gateway_ip()
        if router_ip is None:
            logger.error("Could not determine router IP address.")
            exit(1)

        if PANEL_PASSWORD is None:
            logger.error("Missing required environment variable: PANEL_PASSWORD")
            exit(1)

        panel_password: str = PANEL_PASSWORD

        self.router_ip = router_ip
        self.session = requests.Session()
        self.password = encode.tplink_security_encode(panel_password)
        self.username = PPPOE_USERNAME or ""
        self.pppoe_password = PPPOE_PASSWORD or ""
        self.stok = self.__login_router()

    def __post(self, payload) -> dict:
        router_host = format_ip_for_url_host(self.router_ip)
        url = f"http://{router_host}"
        response = self.session.post(url, json=payload)
        return response.json()

    def __request(self, payload) -> dict:
        router_host = format_ip_for_url_host(self.router_ip)
        url = f"http://{router_host}/stok={self.stok}/ds"
        response = self.session.post(url, json=payload)
        return response.json()

    def __login_router(self) -> str | None:
        payload = {"method": "do", "login": {"password": self.password}}
        response = self.__post(payload)
        if response.get("error_code") == 0 and response.get("stok") is not None:
            return response.get("stok")
        else:
            logger.error("Login failed.")
            logger.debug(response)
            exit(1)
        return None

    def set_credentials(self) -> bool:
        if not self.username or not self.pppoe_password:
            logger.warning(
                "Missing PPPoE credentials override. Will reuse the credentials already saved on the router."
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
            return True
        else:
            logger.error("Failed to set PPPoE credentials.")
            logger.debug(response)
            return False

    def tplink_change_wan_status_request(
        self, action: Literal["connect", "disconnect", "renew"], method: str, proto: str
    ) -> bool:
        payload = {
            "network": {"change_wan_status": {"proto": proto, "operate": action}},
            "method": method,
        }
        response = self.__request(payload)
        if response.get("error_code") == 0:
            return True
        else:
            logger.error("Failed to %s %s.", action, proto)
            logger.debug(response)
            return False

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
            logger.error("Failed to get WAN status.")
            logger.debug(response)
            return {}

    def get_wan_proto(self) -> str | None:
        status = self.tplink_get_wan_status()
        wan_status = status.get("network", {}).get("wan_status", {})
        proto = wan_status.get("proto")
        return proto if isinstance(proto, str) else None

    def make_pppoe_reconnection(self) -> bool:

        if self.username and self.pppoe_password and not self.set_credentials():
            return False

        if not self.tplink_change_wan_status_request(
            action="disconnect", method="do", proto="pppoe"
        ):
            return False
        # Wait for a time to make sure DHCP has assigned a new IP address
        sleep(30)
        if self.tplink_change_wan_status_request(
            action="connect", method="do", proto="pppoe"
        ):
            return True
        return False

    def get_connected_devices(self) -> list:
        payload = {
            "hosts_info": {"table": "host_info", "name": "cap_host_num"},
            "network": {"name": "iface_mac"},
            "hyfi": {"table": ["connected_ext"]},
            "method": "get",
        }
        response = self.__request(payload)
        if response.get("error_code") != 0:
            logger.error("Failed to get connected devices.")
            logger.debug(response)
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

    def dhcp_renew(self) -> bool:
        return self.tplink_change_wan_status_request(
            action="renew", method="do", proto="dhcp"
        )
