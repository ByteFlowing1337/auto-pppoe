import importlib
import unittest
from typing import Any
from unittest.mock import Mock, call, patch


asus_module = importlib.import_module("autodialer.apis.routers.asus.asus_api")
AsusAPI = asus_module.AsusAPI


class TestAsusAPI(unittest.TestCase):
    @patch.object(asus_module, "PANEL_PASSWORD", "panel-password")
    @patch.object(asus_module, "PANEL_USERNAME", "admin")
    @patch.object(asus_module, "get_gateway_ip", return_value="192.168.50.1")
    @patch.object(asus_module.requests, "Session")
    def test_get_wan_proto_uses_active_wan_unit(
        self,
        mock_session_cls: Any,
        _mock_gateway_ip: Any,
    ):
        session = Mock()

        login_response = Mock()
        login_response.raise_for_status.return_value = None
        login_response.json.return_value = {"asus_token": "test-token"}

        status_response = Mock()
        status_response.raise_for_status.return_value = None
        status_response.json.return_value = {
            "get_wan_unit": 1,
            "wan0_proto": "pppoe",
            "wan1_proto": "dhcp",
        }

        session.post.side_effect = [login_response, status_response]
        mock_session_cls.return_value = session

        router = AsusAPI()

        self.assertEqual(router.get_wan_proto(), "dhcp")

    @patch.object(asus_module, "PANEL_PASSWORD", "panel-password")
    @patch.object(asus_module, "PANEL_USERNAME", "admin")
    @patch.object(asus_module, "get_gateway_ip", return_value="192.168.50.1")
    @patch.object(asus_module.requests, "Session")
    def test_dhcp_renew_falls_back_to_restart_wan(
        self,
        mock_session_cls: Any,
        _mock_gateway_ip: Any,
    ):
        session = Mock()

        login_response = Mock()
        login_response.raise_for_status.return_value = None
        login_response.json.return_value = {"asus_token": "test-token"}

        session.post.return_value = login_response
        mock_session_cls.return_value = session

        router = AsusAPI()

        with (
            patch.object(
                router,
                "get_wan_status",
                return_value={"get_wan_unit": 1},
            ),
            patch.object(router, "_run_service", side_effect=[False, True]) as mock_run,
        ):
            self.assertTrue(router.dhcp_renew())

        self.assertEqual(
            mock_run.call_args_list,
            [call("restart_wan1"), call("restart_wan")],
        )

    @patch.object(asus_module, "PANEL_PASSWORD", "panel-password")
    @patch.object(asus_module, "PANEL_USERNAME", "admin")
    @patch.object(asus_module, "get_gateway_ip", return_value="192.168.50.1")
    @patch.object(asus_module.requests, "Session")
    def test_get_connected_devices_filters_offline_clients_and_merges_metadata(
        self,
        mock_session_cls: Any,
        _mock_gateway_ip: Any,
    ):
        session = Mock()

        login_response = Mock()
        login_response.raise_for_status.return_value = None
        login_response.json.return_value = {"asus_token": "test-token"}

        devices_response = Mock()
        devices_response.raise_for_status.return_value = None
        devices_response.text = """
originDataTmp = originData;
originData = {
fromNetworkmapd : [{
    "AA:BB:CC:DD:EE:01": {
        "nickName": "Work Laptop",
        "name": "",
        "ip": "192.168.50.20",
        "mac": "AA:BB:CC:DD:EE:01",
        "isWL": "1",
        "isOnline": "1",
        "isLogin": "1",
        "curTx": "54.4",
        "curRx": "11"
    },
    "AA:BB:CC:DD:EE:02": {
        "nickName": "",
        "name": "",
        "vendor": "",
        "ip": "192.168.50.30",
        "mac": "AA:BB:CC:DD:EE:02",
        "isWL": "0",
        "isOnline": "1",
        "isLogin": "0",
        "curTx": "",
        "curRx": "8"
    },
    "AA:BB:CC:DD:EE:03": {
        "name": "Offline Phone",
        "ip": "192.168.50.40",
        "mac": "AA:BB:CC:DD:EE:03",
        "isWL": "1",
        "isOnline": "0"
    },
    "maclist": ["AA:BB:CC:DD:EE:01", "AA:BB:CC:DD:EE:02"]
}],
nmpClient : [{
    "AA:BB:CC:DD:EE:02": {
        "name": "NAS",
        "vendor": "Synology"
    }
}]
}
networkmap_fullscan = '2';
"""

        session.post.side_effect = [login_response, devices_response]
        mock_session_cls.return_value = session

        router = AsusAPI()

        self.assertEqual(
            router.get_connected_devices(),
            [
                {
                    "hostname": "Work Laptop",
                    "ip": "192.168.50.20",
                    "mac": "AA:BB:CC:DD:EE:01",
                    "type": "wireless",
                    "is_current": True,
                    "up_kbps": 54,
                    "down_kbps": 11,
                },
                {
                    "hostname": "NAS",
                    "ip": "192.168.50.30",
                    "mac": "AA:BB:CC:DD:EE:02",
                    "type": "wired",
                    "is_current": False,
                    "up_kbps": 0,
                    "down_kbps": 8,
                },
            ],
        )

    @patch.object(asus_module, "PANEL_PASSWORD", "panel-password")
    @patch.object(asus_module, "PANEL_USERNAME", "admin")
    @patch.object(asus_module, "get_gateway_ip", return_value="192.168.50.1")
    @patch.object(asus_module.requests, "Session")
    def test_get_connected_devices_returns_empty_list_for_unparseable_payload(
        self,
        mock_session_cls: Any,
        _mock_gateway_ip: Any,
    ):
        session = Mock()

        login_response = Mock()
        login_response.raise_for_status.return_value = None
        login_response.json.return_value = {"asus_token": "test-token"}

        devices_response = Mock()
        devices_response.raise_for_status.return_value = None
        devices_response.text = "invalid payload"

        session.post.side_effect = [login_response, devices_response]
        mock_session_cls.return_value = session

        router = AsusAPI()

        self.assertEqual(router.get_connected_devices(), [])
