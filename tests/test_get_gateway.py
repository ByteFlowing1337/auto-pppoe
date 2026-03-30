import unittest
from unittest.mock import Mock, mock_open, patch
from typing import Any

from autodialer import (
    get_gateway_ip_on_linux,
    get_gateway_ip_on_unix,
    get_gateway_ip_on_windows,
)
from autodialer.apis.utils.get_gateway import format_ip_for_url_host


class TestGetGatewayIp(unittest.TestCase):
    def test_format_ip_for_url_host_ipv4(self):
        self.assertEqual(format_ip_for_url_host("192.168.0.1"), "192.168.0.1")

    def test_format_ip_for_url_host_ipv6(self):
        self.assertEqual(format_ip_for_url_host("2001:db8::1"), "[2001:db8::1]")

    def test_format_ip_for_url_host_scoped_ipv6(self):
        self.assertEqual(format_ip_for_url_host("fe80::1%en0"), "[fe80::1%25en0]")

    @patch("autodialer.apis.utils.get_gateway.subprocess.run")
    def test_windows_gateway_parsed(self, mock_run: Any):
        mock_run.return_value = Mock(
            stdout=(
                "IPv4 Route Table\n"
                "Active Routes:\n"
                "          0.0.0.0          0.0.0.0       192.168.0.1    192.168.0.100     25\n"
            )
        )

        result = get_gateway_ip_on_windows()

        self.assertEqual(result, "192.168.0.1")

    @patch(
        "builtins.open",
        new_callable=mock_open,
        read_data=(
            "Iface\tDestination\tGateway\tFlags\tRefCnt\tUse\tMetric\tMask\tMTU\tWindow\tIRTT\n"
            "eth0\t00000000\t0100000A\t0003\t0\t0\t100\t00000000\t0\t0\t0\n"
        ),
    )
    def test_linux_gateway_parsed(self, _: Any):
        result = get_gateway_ip_on_linux()

        self.assertEqual(result, "10.0.0.1")

    @patch("autodialer.apis.utils.get_gateway.subprocess.run")
    @patch("builtins.open", side_effect=OSError)
    def test_linux_gateway_fallback_parsed(self, _: Any, mock_run: Any):
        mock_run.return_value = Mock(
            stdout="default via 10.0.0.1 dev eth0 proto dhcp src 10.0.0.10\n"
        )

        result = get_gateway_ip_on_linux()

        self.assertEqual(result, "10.0.0.1")

    @patch("autodialer.apis.utils.get_gateway.subprocess.run")
    def test_unix_gateway_parsed(self, mock_run: Any):
        mock_run.return_value = Mock(
            stdout=(
                "   route to: default\n"
                "destination: default\n"
                "    gateway: 172.16.0.1\n"
                "  interface: en0\n"
            )
        )

        result = get_gateway_ip_on_unix()

        self.assertEqual(result, "172.16.0.1")

    @patch("autodialer.apis.utils.get_gateway.subprocess.run")
    def test_no_gateway_returns_none_windows_and_unix(self, mock_run: Any):
        mock_run.side_effect = [
            Mock(stdout=""),
            Mock(stdout=""),
            Mock(stdout=""),
        ]

        self.assertIsNone(get_gateway_ip_on_windows())
        self.assertIsNone(get_gateway_ip_on_unix())

    @patch("autodialer.apis.utils.get_gateway.subprocess.run")
    @patch("builtins.open", side_effect=OSError)
    def test_no_gateway_returns_none_linux(self, _: Any, mock_run: Any):
        mock_run.return_value = Mock(stdout="")

        self.assertIsNone(get_gateway_ip_on_linux())


if __name__ == "__main__":
    unittest.main()
