import importlib
import unittest
from typing import Any
from unittest.mock import Mock, patch


reconnection_module = importlib.import_module("autodialer.reconnection")


class TestParseArguments(unittest.TestCase):
    @patch.object(reconnection_module, "is_target_asn", return_value=True)
    @patch.object(
        reconnection_module,
        "check_isp_with_retries",
        return_value="AS9929 Example ISP",
    )
    @patch("builtins.exit", side_effect=SystemExit(0))
    def test_asn_mode_exits_early_when_already_on_target_asn(
        self, _mock_exit: Any, _mock_check_isp: Any, _mock_is_target_asn: Any
    ):
        with patch.object(
            reconnection_module, "argv", ["autodialer", "--asn", "AS9929"]
        ):
            with self.assertRaises(SystemExit) as context:
                reconnection_module.parse_arguments("AS9929")

        self.assertEqual(context.exception.code, 0)


class TestReconnection(unittest.TestCase):
    def test_get_wan_proto_uses_router_contract(self):
        router = Mock()
        router.get_wan_proto.return_value = "dhcp"

        reconnection = reconnection_module.Reconnection(router)

        self.assertEqual(reconnection._get_wan_proto(), "dhcp")

    def test_apply_reconnection_calls_pppoe_method(self):
        router = Mock()
        router.make_pppoe_reconnection.return_value = True

        reconnection = reconnection_module.Reconnection(router)

        self.assertTrue(reconnection._apply_reconnection("pppoe"))
        router.make_pppoe_reconnection.assert_called_once_with()


if __name__ == "__main__":
    unittest.main()
