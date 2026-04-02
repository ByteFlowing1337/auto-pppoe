import base64
import json
import re
from typing import Any
from urllib.parse import quote

import requests

from autodialer.apis.utils.get_gateway import format_ip_for_url_host, get_gateway_ip
from autodialer.config.config import PANEL_PASSWORD, PANEL_USERNAME

USER_AGENT = "AutoDialer"
REQUEST_TIMEOUT = 5
WAN_STATUS_HOOK = "get_wan_unit();nvram_get(wan0_proto);nvram_get(wan1_proto);"
UPDATE_CLIENTS_PATTERN = re.compile(
    r"originData = (.*)networkmap_fullscan = ",
    re.DOTALL,
)
MAC_ADDRESS_PATTERN = re.compile(r"^(?:[0-9A-Fa-f]{2}:){5}[0-9A-Fa-f]{2}$")


class AsusAPI:
    """Interact with ASUSWRT routers using the web API."""

    SUPPORTED_VENDORS = ("ASUS", "ASUS AiMesh")

    router_ip: str
    panel_username: str
    panel_password: str
    base_url: str
    token: str
    verify_ssl: bool

    def __init__(self):
        router_ip = get_gateway_ip()
        if router_ip is None:
            print("Could not determine router IP address.")
            exit(1)

        if PANEL_PASSWORD is None:
            print("Missing required environment variable: PANEL_PASSWORD")
            exit(1)

        self.router_ip = router_ip
        self.panel_username = PANEL_USERNAME or "admin"
        self.panel_password = PANEL_PASSWORD
        self.session = requests.Session()
        self.base_url, self.verify_ssl, self.token = self._login_router()

    def _candidate_base_urls(self) -> list[tuple[str, bool]]:
        router_host = format_ip_for_url_host(self.router_ip)
        return [
            (f"http://{router_host}", True),
            (f"https://{router_host}", False),
        ]

    @staticmethod
    def _dict_to_request(data: dict[str, Any]) -> str:
        parts: list[str] = []
        for key, value in data.items():
            safe_key = str(key).replace("'", "\\'")
            safe_value = str(value).replace("'", "\\'")
            parts.append(f"'{safe_key}':'{safe_value}'")
        return ";".join(parts)

    @staticmethod
    def _read_json_response(response: requests.Response) -> dict[str, Any] | None:
        try:
            data = response.json()
        except ValueError:
            return None

        return data if isinstance(data, dict) else None

    def _post_request(
        self,
        endpoint: str,
        raw_payload: str,
        form_payload: dict[str, Any] | None = None,
        require_json: bool = True,
        base_url: str | None = None,
        verify_ssl: bool | None = None,
        headers: dict[str, str] | None = None,
    ) -> tuple[bool, dict[str, Any] | None]:
        url = f"{base_url or self.base_url}/{endpoint}"
        ssl_verify = self.verify_ssl if verify_ssl is None else verify_ssl
        payload_variants: list[Any] = [quote(raw_payload)]
        if form_payload is not None:
            payload_variants.append(form_payload)

        last_error: requests.RequestException | None = None

        for payload in payload_variants:
            try:
                response = self.session.post(
                    url,
                    data=payload,
                    headers=headers,
                    timeout=REQUEST_TIMEOUT,
                    verify=ssl_verify,
                )
                response.raise_for_status()
            except requests.RequestException as exc:
                last_error = exc
                continue

            data = self._read_json_response(response)
            if data is None and require_json:
                continue

            return True, data

        if last_error is not None:
            print(f"Error connecting to router: {last_error}")

        return False, None

    def _post_text_request(
        self,
        endpoint: str,
        raw_payload: str,
        form_payload: dict[str, Any] | None = None,
        base_url: str | None = None,
        verify_ssl: bool | None = None,
        headers: dict[str, str] | None = None,
    ) -> tuple[bool, str | None]:
        url = f"{base_url or self.base_url}/{endpoint}"
        ssl_verify = self.verify_ssl if verify_ssl is None else verify_ssl
        payload_variants: list[Any] = [quote(raw_payload)]
        if form_payload is not None:
            payload_variants.append(form_payload)

        last_error: requests.RequestException | None = None

        for payload in payload_variants:
            try:
                response = self.session.post(
                    url,
                    data=payload,
                    headers=headers,
                    timeout=REQUEST_TIMEOUT,
                    verify=ssl_verify,
                )
                response.raise_for_status()
            except requests.RequestException as exc:
                last_error = exc
                continue

            return True, response.text

        if last_error is not None:
            print(f"Error connecting to router: {last_error}")

        return False, None

    @staticmethod
    def _read_dict_json(content: str) -> dict[str, Any]:
        try:
            data = json.loads(content)
        except json.JSONDecodeError:
            return {}

        return data if isinstance(data, dict) else {}

    @classmethod
    def _read_update_clients_data(cls, content: str) -> dict[str, Any]:
        match = UPDATE_CLIENTS_PATTERN.search(content.replace("\n", ""))
        if not match:
            return {}

        payload = re.sub(
            r"\b(fromNetworkmapd|nmpClient)\b\s*:",
            r'"\1":',
            match.group(1),
        )
        return cls._read_dict_json(payload)

    @staticmethod
    def _read_client_map(value: Any) -> dict[str, Any]:
        if isinstance(value, list) and value and isinstance(value[0], dict):
            return value[0]
        if isinstance(value, dict):
            return value
        return {}

    @classmethod
    def _is_mac_address(cls, value: Any) -> bool:
        return (
            isinstance(value, str) and MAC_ADDRESS_PATTERN.fullmatch(value) is not None
        )

    @staticmethod
    def _merge_client_metadata(
        client: dict[str, Any],
        fallback: dict[str, Any] | None,
    ) -> dict[str, Any]:
        if not fallback:
            return client

        merged = client.copy()
        for key in (
            "name",
            "nickName",
            "vendor",
            "vendorclass",
            "type",
            "defaultType",
        ):
            if merged.get(key) in (None, "") and fallback.get(key) not in (
                None,
                "",
            ):
                merged[key] = fallback[key]

        return merged

    @staticmethod
    def _read_device_name(client: dict[str, Any]) -> str:
        for key in ("nickName", "name", "vendor"):
            value = client.get(key)
            if isinstance(value, str):
                value = value.strip()
                if value:
                    return value

        return "(unknown)"

    @staticmethod
    def _read_speed(value: Any) -> int:
        if isinstance(value, (int, float)):
            return max(0, int(round(value)))

        if isinstance(value, str):
            value = value.strip()
            if not value:
                return 0
            try:
                return max(0, int(round(float(value))))
            except ValueError:
                return 0

        return 0

    @staticmethod
    def _is_online(client: dict[str, Any]) -> bool:
        return str(client.get("isOnline", client.get("online", "0"))).strip() == "1"

    @staticmethod
    def _read_connection_type(client: dict[str, Any]) -> str:
        value = client.get(
            "isWL",
            client.get("wireless", client.get("is_wireless", "0")),
        )
        return "wireless" if str(value).strip() not in ("", "0", "None") else "wired"

    def _login_router(self) -> tuple[str, bool, str]:
        auth = f"{self.panel_username}:{self.panel_password}".encode("ascii")
        token_value = base64.b64encode(auth).decode("ascii")
        raw_payload = f"login_authorization={token_value}"
        form_payload = {"login_authorization": token_value}
        headers = {"user-agent": USER_AGENT}

        for base_url, verify_ssl in self._candidate_base_urls():
            ok, data = self._post_request(
                endpoint="login.cgi",
                raw_payload=raw_payload,
                form_payload=form_payload,
                require_json=True,
                base_url=base_url,
                verify_ssl=verify_ssl,
                headers=headers,
            )
            if not ok or not data:
                continue

            token = data.get("asus_token")
            if isinstance(token, str) and token:
                return base_url, verify_ssl, token

        print("Login failed.")
        exit(1)

    def _auth_headers(self) -> dict[str, str]:
        return {
            "user-agent": USER_AGENT,
            "cookie": f"asus_token={self.token}",
        }

    def get_wan_status(self) -> dict[str, Any]:
        ok, data = self._post_request(
            endpoint="appGet.cgi",
            raw_payload=f"hook={WAN_STATUS_HOOK}",
            form_payload={"hook": WAN_STATUS_HOOK},
            require_json=True,
            headers=self._auth_headers(),
        )
        if not ok or not data:
            print("Failed to get ASUS WAN status.")
            return {}

        return data

    @staticmethod
    def _read_wan_unit(status: dict[str, Any]) -> int | None:
        raw_unit = status.get("get_wan_unit")
        if isinstance(raw_unit, int):
            return raw_unit
        if isinstance(raw_unit, str) and raw_unit.isdigit():
            return int(raw_unit)
        return None

    def get_wan_proto(self) -> str | None:
        status = self.get_wan_status()
        if not status:
            return None

        unit = self._read_wan_unit(status)
        candidates: list[Any] = []
        if unit in (0, 1):
            candidates.append(status.get(f"wan{unit}_proto"))
        candidates.extend([status.get("wan0_proto"), status.get("wan1_proto")])

        for proto in candidates:
            if isinstance(proto, str) and proto:
                return proto.lower()

        return None

    def _run_service(self, service: str) -> bool:
        payload = {
            "rc_service": service,
            "action_mode": "apply",
        }
        ok, data = self._post_request(
            endpoint="applyapp.cgi",
            raw_payload=self._dict_to_request(payload),
            form_payload=payload,
            require_json=False,
            headers=self._auth_headers(),
        )
        if not ok:
            return False

        if not data:
            return True

        error_status = data.get("error_status")
        if error_status not in (None, "", 0, "0", False):
            print(f"ASUS service error: {error_status}")
            return False

        run_service = data.get("run_service")
        if not isinstance(run_service, str) or not run_service:
            return True

        accepted_services = {service}
        if service.startswith("restart_wan"):
            accepted_services.add("restart_wan")

        if run_service not in accepted_services:
            print(
                f"Unexpected ASUS service response: expected {service}, got {run_service}."
            )
            return False

        return True

    def _restart_wan(self) -> bool:
        status = self.get_wan_status()
        unit = self._read_wan_unit(status) if status else None

        services_to_try: list[str] = []
        if unit in (0, 1):
            services_to_try.append(f"restart_wan{unit}")
        services_to_try.append("restart_wan")

        for service in services_to_try:
            if self._run_service(service):
                return True

        return False

    def make_pppoe_reconnection(self) -> bool:
        if self._restart_wan():
            return True

        print("Failed to reconnect pppoe.")
        return False

    def dhcp_renew(self) -> bool:
        if self._restart_wan():
            return True

        print("Failed to renew dhcp.")
        return False

    def get_connected_devices(self) -> list[dict[str, Any]]:
        ok, content = self._post_text_request(
            endpoint="update_clients.asp",
            raw_payload="",
            form_payload={},
            headers=self._auth_headers(),
        )
        if not ok or content is None:
            print("Failed to get ASUS connected devices.")
            return []

        data = self._read_update_clients_data(content)
        if not data:
            print("Failed to parse ASUS connected devices.")
            return []

        current_clients = self._read_client_map(data.get("fromNetworkmapd"))
        historical_clients = self._read_client_map(data.get("nmpClient"))

        devices: list[dict[str, Any]] = []
        for mac, client in current_clients.items():
            if not self._is_mac_address(mac) or not isinstance(client, dict):
                continue

            fallback = historical_clients.get(mac)
            merged_client = self._merge_client_metadata(
                client,
                fallback if isinstance(fallback, dict) else None,
            )
            if not self._is_online(merged_client):
                continue

            devices.append(
                {
                    "hostname": self._read_device_name(merged_client),
                    "ip": merged_client.get("ip", "-") or "-",
                    "mac": mac,
                    "type": self._read_connection_type(merged_client),
                    "is_current": str(merged_client.get("isLogin", "0")).strip() == "1",
                    "up_kbps": self._read_speed(merged_client.get("curTx")),
                    "down_kbps": self._read_speed(merged_client.get("curRx")),
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
