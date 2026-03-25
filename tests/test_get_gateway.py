import unittest
from unittest.mock import Mock, patch
from typing import Any

from autodialer.apis.get_gateway import (
    get_gateway_ip_on_linux,
    get_gateway_ip_on_unix,
    get_gateway_ip_on_windows,
)


class TestGetGatewayIp(unittest.TestCase):
    @patch("autodialer.apis.get_gateway.subprocess.run")
    def test_windows_gateway_parsed(self, mock_run: Any):
        mock_run.return_value = Mock(
            stdout="Ethernet adapter:\n   Default Gateway . . . . . . . . . : 192.168.0.1\n"
        )

        result = get_gateway_ip_on_windows()

        self.assertEqual(result, "192.168.0.1")

    @patch("autodialer.apis.get_gateway.subprocess.run")
    def test_linux_gateway_parsed(self, mock_run: Any):
        mock_run.return_value = Mock(stdout="default via 10.0.0.1 dev eth0 proto dhcp\n")

        result = get_gateway_ip_on_linux()

        self.assertEqual(result, "10.0.0.1")

    @patch("autodialer.apis.get_gateway.subprocess.run")
    def test_unix_gateway_parsed(self, mock_run: Any):
        mock_run.return_value = Mock(stdout="default 172.16.0.1 UGSc 46 0 en0\n")

        result = get_gateway_ip_on_unix()

        self.assertEqual(result, "172.16.0.1")

    @patch("autodialer.apis.get_gateway.subprocess.run")
    def test_no_gateway_returns_none(self, mock_run: Any):
        mock_run.return_value = Mock(stdout="")

        self.assertIsNone(get_gateway_ip_on_windows())
        self.assertIsNone(get_gateway_ip_on_linux())
        self.assertIsNone(get_gateway_ip_on_unix())


if __name__ == "__main__":
    unittest.main()