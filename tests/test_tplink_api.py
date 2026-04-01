import importlib
import unittest
from typing import Any
from unittest.mock import Mock, patch


tplink_module = importlib.import_module("autodialer.apis.routers.tplink.tplink_api")
TPLinkAPI = tplink_module.TPLinkAPI


class TestTPLinkAPI(unittest.TestCase):
    @patch.object(tplink_module, "PANEL_PASSWORD", "panel-password")
    @patch.object(tplink_module, "PPPOE_USERNAME", None)
    @patch.object(tplink_module, "PPPOE_PASSWORD", None)
    @patch.object(tplink_module, "get_gateway_ip", return_value="192.168.0.1")
    @patch.object(tplink_module.requests, "Session")
    def test_pppoe_reconnect_reuses_saved_credentials_when_override_missing(
        self,
        mock_session_cls: Any,
        _mock_gateway_ip: Any,
    ):
        session = Mock()
        login_response = {"error_code": 0, "stok": "stok"}
        disconnect_response = {"error_code": 0}
        connect_response = {"error_code": 0}
        session.post.return_value.json.side_effect = [
            login_response,
            disconnect_response,
            connect_response,
        ]
        mock_session_cls.return_value = session

        router = TPLinkAPI()

        with patch.object(tplink_module, "sleep") as mock_sleep:
            result = router.make_pppoe_reconnection()

        self.assertTrue(result)
        mock_sleep.assert_called_once_with(30)

    @patch.object(tplink_module, "PANEL_PASSWORD", "panel-password")
    @patch.object(tplink_module, "PPPOE_USERNAME", "campus-user")
    @patch.object(tplink_module, "PPPOE_PASSWORD", "campus-pass")
    @patch.object(tplink_module, "get_gateway_ip", return_value="192.168.0.1")
    @patch.object(tplink_module.requests, "Session")
    def test_pppoe_reconnect_updates_credentials_when_override_present(
        self,
        mock_session_cls: Any,
        _mock_gateway_ip: Any,
    ):
        session = Mock()
        login_response = {"error_code": 0, "stok": "stok"}
        set_response = {"error_code": 0}
        disconnect_response = {"error_code": 0}
        connect_response = {"error_code": 0}
        session.post.return_value.json.side_effect = [
            login_response,
            set_response,
            disconnect_response,
            connect_response,
        ]
        mock_session_cls.return_value = session

        router = TPLinkAPI()

        with patch.object(tplink_module, "sleep") as mock_sleep:
            result = router.make_pppoe_reconnection()

        self.assertTrue(result)
        mock_sleep.assert_called_once_with(30)

    @patch.object(tplink_module, "PANEL_PASSWORD", "panel-password")
    @patch.object(tplink_module, "PPPOE_USERNAME", "campus-user")
    @patch.object(tplink_module, "PPPOE_PASSWORD", "campus-pass")
    @patch.object(tplink_module, "get_gateway_ip", return_value="192.168.0.1")
    @patch.object(tplink_module.requests, "Session")
    def test_pppoe_reconnect_stops_when_credential_update_fails(
        self,
        mock_session_cls: Any,
        _mock_gateway_ip: Any,
    ):
        session = Mock()
        login_response = {"error_code": 0, "stok": "stok"}
        failed_set_response = {"error_code": 1}
        session.post.return_value.json.side_effect = [
            login_response,
            failed_set_response,
        ]
        mock_session_cls.return_value = session

        router = TPLinkAPI()

        with (
            patch.object(tplink_module, "sleep") as mock_sleep,
            patch.object(
                router,
                "tplink_change_wan_status_request",
                wraps=router.tplink_change_wan_status_request,
            ) as mock_change_status,
        ):
            result = router.make_pppoe_reconnection()

        self.assertFalse(result)
        mock_sleep.assert_not_called()
        mock_change_status.assert_not_called()
