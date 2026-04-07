import importlib
import unittest
from typing import Any
from unittest.mock import Mock, patch

import requests


check_vendor_module = importlib.import_module("autodialer.apis.utils.check_vendor")


class TestCheckRouterVendor(unittest.TestCase):
    @staticmethod
    def _build_response(
        *,
        text: str = "",
        headers: dict[str, str] | None = None,
        url: str = "http://192.168.0.1/",
        history: list[Mock] | None = None,
    ) -> Mock:
        response = Mock()
        response.text = text
        response.headers = headers or {}
        response.url = url
        response.history = history or []
        response.raise_for_status.return_value = None
        return response

    @patch.object(check_vendor_module, "get_gateway_ip", return_value="192.168.0.1")
    @patch.object(check_vendor_module.requests, "get")
    def test_detects_vendor_from_uppercase_html_title(
        self,
        mock_get: Any,
        _mock_gateway: Any,
    ):
        mock_get.return_value = self._build_response(
            text="<html><HEAD><TITLE>ASUS Router</TITLE></HEAD></html>"
        )

        vendor = check_vendor_module.check_router_vendor()

        self.assertEqual(vendor, "ASUS")
        mock_get.assert_called_once_with("http://192.168.0.1", timeout=5)

    @patch.object(check_vendor_module, "get_gateway_ip", return_value="192.168.0.1")
    @patch.object(check_vendor_module.requests, "get")
    def test_detects_vendor_from_body_when_title_missing(
        self,
        mock_get: Any,
        _mock_gateway: Any,
    ):
        mock_get.return_value = self._build_response(
            text="<html><body>Powered by ZTE home gateway firmware</body></html>"
        )

        vendor = check_vendor_module.check_router_vendor()

        self.assertEqual(vendor, "ZTE")

    @patch.object(check_vendor_module, "get_gateway_ip", return_value="192.168.0.1")
    @patch.object(check_vendor_module.requests, "get")
    def test_detects_vendor_from_redirect_location_header(
        self,
        mock_get: Any,
        _mock_gateway: Any,
    ):
        redirect_response = self._build_response(
            headers={"Location": "http://tplinkwifi.net/webpages/index.html"},
            url="http://192.168.0.1/",
        )
        mock_get.return_value = self._build_response(
            text="<html><body>login</body></html>",
            history=[redirect_response],
        )

        vendor = check_vendor_module.check_router_vendor()

        self.assertEqual(vendor, "TP-Link")

    @patch.object(check_vendor_module, "get_gateway_ip", return_value="192.168.0.1")
    @patch.object(check_vendor_module.requests, "get")
    def test_detects_vendor_from_response_headers(
        self,
        mock_get: Any,
        _mock_gateway: Any,
    ):
        mock_get.return_value = self._build_response(
            headers={"Server": "MikroTik RouterOS"},
            text="<html><body>login</body></html>",
        )

        vendor = check_vendor_module.check_router_vendor()

        self.assertEqual(vendor, "MikroTik")

    @patch.object(check_vendor_module.requests, "get")
    @patch.object(check_vendor_module, "get_gateway_ip", return_value=None)
    def test_returns_none_when_gateway_is_unavailable(
        self,
        _mock_gateway: Any,
        mock_get: Any,
    ):
        vendor = check_vendor_module.check_router_vendor()

        self.assertIsNone(vendor)
        mock_get.assert_not_called()

    @patch.object(check_vendor_module, "get_gateway_ip", return_value="192.168.0.1")
    @patch.object(
        check_vendor_module.requests,
        "get",
        side_effect=requests.RequestException("boom"),
    )
    def test_returns_none_when_router_request_fails(
        self,
        _mock_get: Any,
        _mock_gateway: Any,
    ):
        vendor = check_vendor_module.check_router_vendor()

        self.assertIsNone(vendor)


if __name__ == "__main__":
    unittest.main()
