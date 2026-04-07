import logging
import re
from typing import Any
from xml.etree import ElementTree as ET

import requests

from autodialer.apis.routers.base_api import RouterAPI
from autodialer.apis.utils.get_gateway import get_gateway_ip, format_ip_for_url_host
from autodialer.config.config import PANEL_PASSWORD, PANEL_USERNAME
from autodialer.encode.zte_encode import zte_security_encode

logger = logging.getLogger(__name__)


class ZteApi(RouterAPI):
    SUPPORTED_VENDORS = ("ZTE",)
    BROWSER_USER_AGENT = (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/146.0.0.0 Safari/537.36"
    )

    def __init__(self):
        router_ip = get_gateway_ip()
        if router_ip is None:
            logger.error("Could not determine router IP address.")
            exit(1)
        self.router_host = format_ip_for_url_host(router_ip)
        self.session = requests.Session()
        self._seed_browser_cookies()
        if not self._authenticate():
            logger.error("Failed to login to router.")
            exit(1)

    def _seed_browser_cookies(self) -> None:
        self.session.headers.update(
            {
                "User-Agent": ZteApi.BROWSER_USER_AGENT,
                "Accept-Language": "en-US,en;q=0.9,zh-TW;q=0.8,zh;q=0.7",
            }
        )

        self.session.cookies.set(
            "_TESTCOOKIESUPPORT",
            "1",
            domain=self.router_host,
            path="/",
        )
        self.session.cookies.set(
            "sidebarStatus",
            "0",
            domain=self.router_host,
            path="/",
        )

    def _authenticate(self) -> bool:
        data = self._get_session_token()
        if data is None:
            logger.error("Failed to retrieve session token.")
            return False

        self.logintoken = data.get("logintoken")
        self.sessiontoken = data.get("_sessionToken")
        if self.logintoken is None or self.sessiontoken is None:
            logger.error("Router did not return the expected login tokens.")
            return False

        if PANEL_PASSWORD is None:
            logger.error(
                "ZTE router authentication failed: PANEL_PASSWORD is not configured."
            )
            return False
        self.password = zte_security_encode(PANEL_PASSWORD, self.logintoken)
        authenticated_session_token = self._login_router()
        if authenticated_session_token is None:
            return False

        self.sessiontoken = authenticated_session_token
        return True

    def _has_sid_cookie(self) -> bool:
        return bool(
            self.session.cookies.get("SID", domain=self.router_host, path="/")
            or self.session.cookies.get("SID")
        )

    def _get_session_token(self) -> dict | None:
        url = f"http://{self.router_host}"
        parameters = {"_type": "loginsceneData", "_tag": "login_token_json"}
        try:
            response = self.session.get(url, params=parameters, timeout=5)
            response.raise_for_status()
            data = response.json()
            if not isinstance(data, dict):
                logger.error("Unexpected session token payload from router.")
                return None
            return data
        except requests.RequestException as e:
            logger.error(f"Failed to get session token: {e}")
            return None
        except ValueError as e:
            logger.error(f"Failed to decode session token response: {e}")
            return None

    def _login_router(self) -> str | None:
        url = f"http://{self.router_host}"
        parameters = {"_type": "loginData", "_tag": "login_entry"}

        payload = {
            "Username": PANEL_USERNAME,
            "Password": self.password,
            "action": "login",
            "Frm_Logintoken": self.logintoken,
            "captchaCode": "",
            "_sessionTOKEN": self.sessiontoken,
            "_sessionToken": self.sessiontoken,
        }

        try:
            response = self.session.post(
                url, params=parameters, data=payload, timeout=5
            )
            response.raise_for_status()
            data = response.json()
            if not isinstance(data, dict):
                logger.error("Unexpected login payload from router.")
                return None

            login_error = data.get("loginErrMsg")
            if login_error:
                logger.error(f"Login failed: {login_error}")
                return None

            if not self._has_sid_cookie():
                logger.error("Router login succeeded but no SID cookie was stored.")
                return None

            return data.get("sess_token")
        except requests.RequestException as e:
            logger.error(f"Failed to login: {e}")
            return None
        except ValueError as e:
            logger.error(f"Failed to decode login response: {e}")
            return None

    def _get_xsrf_token(self) -> str | None:
        url = f"http://{self.router_host}"
        parameters = {"_type": "hiddenData", "_tag": "vue_userif_data"}
        headers = {
            "Accept": "*/*",
            "Origin": f"http://{self.router_host}",
            "Referer": f"http://{self.router_host}/",
        }

        try:
            response = self.session.get(
                url,
                params=parameters,
                headers=headers,
                timeout=5,
            )
            response.raise_for_status()
            xsrf_token = response.headers.get("x_xsrf_token")
            if xsrf_token:
                return xsrf_token.strip()

            logger.error("Router did not return x_xsrf_token for vue_userif_data.")
            return None
        except requests.RequestException as e:
            logger.error(f"Failed to get x_xsrf_token: {e}")
            return None

    def _parse_router_xml_response(self, body: str) -> dict[str, str] | None:
        stripped_body = body.strip()
        if not stripped_body.startswith("<"):
            return None

        try:
            root = ET.fromstring(stripped_body)
        except ET.ParseError:
            return None

        parsed: dict[str, str] = {}
        for field_name in (
            "IF_ERRORPARAM",
            "IF_ERRORTYPE",
            "IF_ERRORSTR",
            "IF_ERRORID",
        ):
            field = root.find(field_name)
            if field is not None and field.text is not None:
                parsed[field_name] = field.text.strip()

        return parsed

    @staticmethod
    def _read_xml_instance(instance: ET.Element) -> dict[str, str]:
        values: dict[str, str] = {}
        children = list(instance)
        index = 0
        while index + 1 < len(children):
            name_node = children[index]
            value_node = children[index + 1]
            if name_node.tag == "ParaName" and value_node.tag == "ParaValue":
                key = (name_node.text or "").strip()
                if key:
                    values[key] = (value_node.text or "").strip()
                index += 2
                continue
            index += 1
        return values

    @staticmethod
    def _read_speed(value: str | None) -> int:
        if value is None:
            return 0
        try:
            return max(0, int(float(value.strip() or "0")))
        except ValueError:
            return 0

    @staticmethod
    def _is_active_device(instance: dict[str, str]) -> bool:
        return instance.get("Active", "").strip() == "1"

    @staticmethod
    def _read_device_name(instance: dict[str, str]) -> str:
        for key in ("HostName", "DevName", "AliasName", "ParentDeviceName"):
            value = instance.get(key, "").strip()
            if value:
                return value
        return "(unknown)"

    @staticmethod
    def _read_connection_type(instance: dict[str, str]) -> str:
        interface = instance.get("Interface", "").strip().lower()
        band = instance.get("Band", "").strip()
        connect_type = instance.get("ConnectType", "").strip()
        interface_type = instance.get("InterfaceType", "").strip()
        if (
            connect_type == "1"
            or interface.startswith("wlan")
            or interface_type == "3"
            or bool(band)
        ):
            return "wireless"
        return "wired"

    @staticmethod
    def _is_current_device(instance: dict[str, str]) -> bool:
        local_mac = instance.get("LocalMacAddr", "").strip().lower()
        mac = instance.get("MACAddress", "").strip().lower()
        return bool(local_mac and mac and local_mac == mac)

    def get_wan_proto(self) -> str | None:
        url = f"http://{self.router_host}/?_type=vueData&_tag=home_internetreg_lua"
        try:
            response = self.session.get(url, timeout=5)
            response.raise_for_status()
            pattern = (
                r"<ParaName>Addressingtype</ParaName>\s*<ParaValue>(.*?)</ParaValue>"
            )
            match = re.search(pattern, response.text)

            wan_proto = match.group(1) if match else None
            if wan_proto is None:
                logger.error("WAN protocol not found in response.")
                return None

            if wan_proto:
                return wan_proto.lower()

            logger.error("WAN_PROTO not found in response.")
            return None
        except requests.RequestException as e:
            logger.error(f"Failed to get WAN protocol: {e}")
            return None

    def make_pppoe_reconnection(self) -> bool:
        first_attempt = self._restart_once()
        if first_attempt == "success":
            return True
        if first_attempt != "expired":
            return False

        if not self._authenticate():
            logger.error("Failed to refresh router session.")
            return False
        return self._restart_once() == "success"

    def _restart_once(self) -> str:
        url = f"http://{self.router_host}"
        parameters = {"_type": "vueData", "_tag": "vue_derestart_data"}
        xsrf_token = self._get_xsrf_token()
        if xsrf_token is None:
            return "failed"

        payload = {
            "IF_ACTION": "Restart",
            "_sessionTOKEN": xsrf_token,
        }
        headers = {
            "Accept": "*/*",
            "Origin": f"http://{self.router_host}",
            "Referer": f"http://{self.router_host}/",
        }

        try:
            response = self.session.post(
                url,
                params=parameters,
                headers=headers,
                data=payload,
                timeout=5,
            )
            response.raise_for_status()
            body = response.text.strip()

            xml_response = self._parse_router_xml_response(body)
            if xml_response is not None:
                error_id = xml_response.get("IF_ERRORID", "")
                error_message = xml_response.get("IF_ERRORSTR", "")

                if error_id == "-1452":
                    logger.warning(
                        "Router session expired during DHCP renew: %s",
                        error_message or "page expired",
                    )
                    return "expired"

                if xml_response.get(
                    "IF_ERRORPARAM", ""
                ).upper() == "SUCC" and error_id in {
                    "",
                    "0",
                }:
                    logger.info("DHCP renew successful.")
                    return "success"

                logger.error(
                    "Restart failed: %s",
                    error_message or "unexpected XML response from router.",
                )
                return "failed"
            if "json" in response.headers.get(
                "Content-Type", ""
            ).lower() or body.startswith("{"):
                try:
                    data = response.json()
                    if isinstance(data, dict) and data.get("SUCC"):
                        logger.info("DHCP renew successful.")
                        return "success"
                except ValueError:
                    logger.error("Failed to parse JSON response.")
                    return "failed"

                logger.error("Restart failed: Unexpected JSON response.")
                return "failed"

            lowered_body = body.lower()
            if "succ" in lowered_body or "success" in lowered_body:
                logger.info("DHCP renew successful.")
                return "success"

            if "<html" in lowered_body or "<!doctype" in lowered_body:
                logger.error(
                    "Restart failed: Router returned HTML instead of API data."
                )
                return "failed"

            return "success"
        except requests.RequestException as e:
            logger.error(f"Failed to restart: {e}")
            return "failed"

    def dhcp_renew(self) -> bool:
        first_attempt = self._restart_once()
        if first_attempt == "success":
            return True
        if first_attempt != "expired":
            return False

        if not self._authenticate():
            logger.error("Failed to refresh router session.")
            return False

        return self._restart_once() == "success"

    def get_connected_devices(self) -> list[dict[str, Any]]:
        url = f"http://{self.router_host}"
        parameters = {"_type": "vueData", "_tag": "localnet_lan_info_lua"}
        try:
            response = self.session.get(url, params=parameters, timeout=5)
            response.raise_for_status()
        except requests.RequestException as e:
            logger.error(f"Failed to get connected devices: {e}")
            return []

        try:
            root = ET.fromstring(response.text.strip())
        except ET.ParseError:
            logger.error("Failed to parse ZTE connected devices.")
            return []

        lan_info = root.find("OBJ_LAN_INFO_ID")
        if lan_info is None:
            logger.error("Failed to locate ZTE LAN info payload.")
            return []

        devices: list[dict[str, Any]] = []
        for instance_node in lan_info.findall("Instance"):
            instance = self._read_xml_instance(instance_node)
            if not self._is_active_device(instance):
                continue

            mac = instance.get("MACAddress", "").strip() or "-"
            devices.append(
                {
                    "hostname": self._read_device_name(instance),
                    "ip": instance.get("IPAddress", "").strip() or "-",
                    "mac": mac,
                    "type": self._read_connection_type(instance),
                    "is_current": self._is_current_device(instance),
                    "up_kbps": self._read_speed(instance.get("UploadSpeed")),
                    "down_kbps": self._read_speed(instance.get("DownloadSpeed")),
                }
            )

        devices.sort(
            key=lambda device: (
                not device["is_current"],
                device["hostname"].lower(),
                device["mac"],
            )
        )
        return devices
