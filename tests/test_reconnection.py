import importlib
import unittest
from typing import Any
from unittest.mock import patch


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


if __name__ == "__main__":
    unittest.main()
