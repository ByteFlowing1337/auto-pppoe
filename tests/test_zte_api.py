import importlib
import unittest
from typing import Any
from unittest.mock import Mock, call, patch

import requests


zte_module = importlib.import_module("autodialer.apis.routers.zte.zte_api")
ZteApi = zte_module.ZteApi


class TestZteApi(unittest.TestCase):
    @patch.object(zte_module, "PANEL_USERNAME", "admin")
    @patch.object(zte_module, "PANEL_PASSWORD", "panel-password")
    @patch.object(zte_module, "get_gateway_ip", return_value="192.168.5.1")
    @patch.object(zte_module, "zte_security_encode", return_value="encoded-password")
    @patch.object(zte_module.requests, "Session")
    def test_get_wan_proto_uses_authenticated_session_cookie(
        self,
        mock_session_cls: Any,
        _mock_encode: Any,
        _mock_gateway_ip: Any,
    ):
        session = Mock()
        session.cookies = requests.cookies.RequestsCookieJar()

        token_response = Mock()
        token_response.raise_for_status.return_value = None
        token_response.json.return_value = {
            "logintoken": "login-token",
            "_sessionToken": "pre-auth-session",
        }

        login_response = Mock()
        login_response.raise_for_status.return_value = None
        login_response.json.return_value = {
            "loginErrMsg": "",
            "sess_token": "post-auth-session",
        }

        status_response = Mock()
        status_response.raise_for_status.return_value = None
        status_response.text = (
            "<ParaName>Addressingtype</ParaName><ParaValue>DHCP</ParaValue>"
        )

        def post_side_effect(*args: Any, **kwargs: Any):
            session.cookies.set("SID", "sid-value", domain="192.168.5.1", path="/")
            return login_response

        session.get.side_effect = [token_response, status_response]
        session.post.side_effect = post_side_effect
        mock_session_cls.return_value = session

        router = ZteApi()

        self.assertEqual(router.get_wan_proto(), "dhcp")
        self.assertEqual(router.sessiontoken, "post-auth-session")
        self.assertEqual(
            session.cookies.get("_TESTCOOKIESUPPORT", domain="192.168.5.1", path="/"),
            "1",
        )
        self.assertEqual(
            session.cookies.get("sidebarStatus", domain="192.168.5.1", path="/"),
            "0",
        )
        self.assertEqual(
            session.post.call_args,
            call(
                "http://192.168.5.1",
                params={"_type": "loginData", "_tag": "login_entry"},
                data={
                    "Username": "admin",
                    "Password": "encoded-password",
                    "action": "login",
                    "Frm_Logintoken": "login-token",
                    "captchaCode": "",
                    "_sessionTOKEN": "pre-auth-session",
                    "_sessionToken": "pre-auth-session",
                },
                timeout=5,
            ),
        )
        self.assertEqual(
            session.get.call_args_list[1],
            call(
                "http://192.168.5.1/?_type=vueData&_tag=home_internetreg_lua", timeout=5
            ),
        )

    @patch.object(zte_module, "PANEL_USERNAME", "admin")
    @patch.object(zte_module, "PANEL_PASSWORD", "panel-password")
    @patch.object(zte_module, "get_gateway_ip", return_value="192.168.5.1")
    @patch.object(zte_module, "zte_security_encode", return_value="encoded-password")
    @patch.object(zte_module.requests, "Session")
    def test_dhcp_renew_uses_authenticated_session_token(
        self,
        mock_session_cls: Any,
        _mock_encode: Any,
        _mock_gateway_ip: Any,
    ):
        session = Mock()
        session.cookies = requests.cookies.RequestsCookieJar()

        token_response = Mock()
        token_response.raise_for_status.return_value = None
        token_response.json.return_value = {
            "logintoken": "login-token",
            "_sessionToken": "pre-auth-session",
        }

        login_response = Mock()
        login_response.raise_for_status.return_value = None
        login_response.json.return_value = {
            "loginErrMsg": "",
            "sess_token": "post-auth-session",
        }

        hidden_data_response = Mock()
        hidden_data_response.raise_for_status.return_value = None
        hidden_data_response.headers = {"x_xsrf_token": "xsrf-token-value"}

        restart_response = Mock()
        restart_response.raise_for_status.return_value = None
        restart_response.text = ""
        restart_response.headers = {"Content-Type": "text/plain"}

        responses = [login_response, restart_response]

        def post_side_effect(*args: Any, **kwargs: Any):
            response = responses.pop(0)
            if response is login_response:
                session.cookies.set("SID", "sid-value", domain="192.168.5.1", path="/")
            return response

        session.get.side_effect = [token_response, hidden_data_response]
        session.post.side_effect = post_side_effect
        mock_session_cls.return_value = session

        router = ZteApi()

        self.assertTrue(router.dhcp_renew())
        self.assertEqual(
            session.post.call_args_list[1],
            call(
                "http://192.168.5.1",
                params={"_type": "vueData", "_tag": "vue_derestart_data"},
                headers={
                    "Accept": "*/*",
                    "Origin": "http://192.168.5.1",
                    "Referer": "http://192.168.5.1/",
                },
                data={
                    "IF_ACTION": "Restart",
                    "_sessionTOKEN": "xsrf-token-value",
                },
                timeout=5,
            ),
        )
        self.assertEqual(
            session.get.call_args_list[1],
            call(
                "http://192.168.5.1",
                params={"_type": "hiddenData", "_tag": "vue_userif_data"},
                headers={
                    "Accept": "*/*",
                    "Origin": "http://192.168.5.1",
                    "Referer": "http://192.168.5.1/",
                },
                timeout=5,
            ),
        )

    @patch.object(zte_module, "PANEL_USERNAME", "admin")
    @patch.object(zte_module, "PANEL_PASSWORD", "panel-password")
    @patch.object(zte_module, "get_gateway_ip", return_value="192.168.5.1")
    @patch.object(zte_module, "zte_security_encode", return_value="encoded-password")
    @patch.object(zte_module.requests, "Session")
    def test_dhcp_renew_rejects_html_response(
        self,
        mock_session_cls: Any,
        _mock_encode: Any,
        _mock_gateway_ip: Any,
    ):
        session = Mock()
        session.cookies = requests.cookies.RequestsCookieJar()

        token_response = Mock()
        token_response.raise_for_status.return_value = None
        token_response.json.return_value = {
            "logintoken": "login-token",
            "_sessionToken": "pre-auth-session",
        }

        login_response = Mock()
        login_response.raise_for_status.return_value = None
        login_response.json.return_value = {
            "loginErrMsg": "",
            "sess_token": "post-auth-session",
        }

        hidden_data_response = Mock()
        hidden_data_response.raise_for_status.return_value = None
        hidden_data_response.headers = {"x_xsrf_token": "xsrf-token-value"}

        restart_response = Mock()
        restart_response.raise_for_status.return_value = None
        restart_response.text = "<html>login</html>"
        restart_response.headers = {"Content-Type": "text/html"}

        responses = [login_response, restart_response]

        def post_side_effect(*args: Any, **kwargs: Any):
            response = responses.pop(0)
            if response is login_response:
                session.cookies.set("SID", "sid-value", domain="192.168.5.1", path="/")
            return response

        session.get.side_effect = [token_response, hidden_data_response]
        session.post.side_effect = post_side_effect
        mock_session_cls.return_value = session

        router = ZteApi()

        self.assertFalse(router.dhcp_renew())

    @patch.object(zte_module, "PANEL_USERNAME", "admin")
    @patch.object(zte_module, "PANEL_PASSWORD", "panel-password")
    @patch.object(zte_module, "get_gateway_ip", return_value="192.168.5.1")
    @patch.object(zte_module, "zte_security_encode", return_value="encoded-password")
    @patch.object(zte_module.requests, "Session")
    def test_dhcp_renew_refreshes_auth_when_router_reports_expired_page(
        self,
        mock_session_cls: Any,
        _mock_encode: Any,
        _mock_gateway_ip: Any,
    ):
        session = Mock()
        session.cookies = requests.cookies.RequestsCookieJar()

        initial_token_response = Mock()
        initial_token_response.raise_for_status.return_value = None
        initial_token_response.json.return_value = {
            "logintoken": "login-token-1",
            "_sessionToken": "pre-auth-session-1",
        }

        refreshed_token_response = Mock()
        refreshed_token_response.raise_for_status.return_value = None
        refreshed_token_response.json.return_value = {
            "logintoken": "login-token-2",
            "_sessionToken": "pre-auth-session-2",
        }

        initial_login_response = Mock()
        initial_login_response.raise_for_status.return_value = None
        initial_login_response.json.return_value = {
            "loginErrMsg": "",
            "sess_token": "post-auth-session-1",
        }

        initial_hidden_data_response = Mock()
        initial_hidden_data_response.raise_for_status.return_value = None
        initial_hidden_data_response.headers = {"x_xsrf_token": "xsrf-token-1"}

        refreshed_login_response = Mock()
        refreshed_login_response.raise_for_status.return_value = None
        refreshed_login_response.json.return_value = {
            "loginErrMsg": "",
            "sess_token": "post-auth-session-2",
        }

        refreshed_hidden_data_response = Mock()
        refreshed_hidden_data_response.raise_for_status.return_value = None
        refreshed_hidden_data_response.headers = {"x_xsrf_token": "xsrf-token-2"}

        expired_restart_response = Mock()
        expired_restart_response.raise_for_status.return_value = None
        expired_restart_response.text = (
            "<ajax_response_xml_root>"
            "<IF_ERRORPARAM>SUCC</IF_ERRORPARAM>"
            "<IF_ERRORTYPE>-1</IF_ERRORTYPE>"
            "<IF_ERRORSTR>页面过期，请刷新后重试。</IF_ERRORSTR>"
            "<IF_ERRORID>-1452</IF_ERRORID>"
            "</ajax_response_xml_root>"
        )
        expired_restart_response.headers = {"Content-Type": "text/xml"}

        successful_restart_response = Mock()
        successful_restart_response.raise_for_status.return_value = None
        successful_restart_response.text = ""
        successful_restart_response.headers = {"Content-Type": "text/plain"}

        session.get.side_effect = [
            initial_token_response,
            initial_hidden_data_response,
            refreshed_token_response,
            refreshed_hidden_data_response,
        ]

        responses = [
            initial_login_response,
            expired_restart_response,
            refreshed_login_response,
            successful_restart_response,
        ]

        def post_side_effect(*args: Any, **kwargs: Any):
            response = responses.pop(0)
            if response is initial_login_response:
                session.cookies.set(
                    "SID", "sid-value-1", domain="192.168.5.1", path="/"
                )
            if response is refreshed_login_response:
                session.cookies.set(
                    "SID", "sid-value-2", domain="192.168.5.1", path="/"
                )
            return response

        session.post.side_effect = post_side_effect
        mock_session_cls.return_value = session

        router = ZteApi()

        self.assertTrue(router.dhcp_renew())
        self.assertEqual(
            session.post.call_args_list[3],
            call(
                "http://192.168.5.1",
                params={"_type": "vueData", "_tag": "vue_derestart_data"},
                headers={
                    "Accept": "*/*",
                    "Origin": "http://192.168.5.1",
                    "Referer": "http://192.168.5.1/",
                },
                data={
                    "IF_ACTION": "Restart",
                    "_sessionTOKEN": "xsrf-token-2",
                },
                timeout=5,
            ),
        )
