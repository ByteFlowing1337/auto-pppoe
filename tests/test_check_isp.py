import unittest
from unittest.mock import Mock, patch
from typing import Any

import requests

from autodialer.apis.check_isp import check_isp, check_isp_with_retries


class TestCheckIsp(unittest.TestCase):
    @patch("autodialer.apis.check_isp.requests.get")
    def test_check_isp_success_returns_org(self, mock_get: Any):
        response = Mock()
        response.raise_for_status.return_value = None
        response.json.return_value = {"org": "AS1234 Example ISP"}
        mock_get.return_value = response

        result = check_isp()

        self.assertEqual(result, "AS1234 Example ISP")

    @patch("autodialer.apis.check_isp.requests.get", side_effect=requests.Timeout)
    def test_check_isp_timeout_returns_none(self, _mock_get: Any):
        result = check_isp()
        self.assertIsNone(result)

    @patch("autodialer.apis.check_isp.requests.get")
    def test_check_isp_invalid_payload_returns_none(self, mock_get: Any):
        response = Mock()
        response.raise_for_status.return_value = None
        response.json.return_value = {"unexpected": "value"}
        mock_get.return_value = response

        result = check_isp()

        self.assertIsNone(result)


class TestCheckIspWithRetries(unittest.TestCase):
    @patch("autodialer.apis.check_isp.time.sleep")
    @patch("autodialer.apis.check_isp.check_isp", side_effect=[None, None, "AS9999 Retry ISP"])
    def test_retries_until_success(self, mock_check_isp: Any, mock_sleep: Any):
        result = check_isp_with_retries(retries=3, delay=1)

        self.assertEqual(result, "AS9999 Retry ISP")
        self.assertEqual(mock_check_isp.call_count, 3)
        self.assertEqual(mock_sleep.call_count, 2)

    @patch("autodialer.apis.check_isp.time.sleep")
    @patch("autodialer.apis.check_isp.check_isp", return_value=None)
    def test_returns_none_after_all_retries(self, mock_check_isp: Any, mock_sleep: Any):
        result = check_isp_with_retries(retries=2, delay=1)

        self.assertIsNone(result)
        self.assertEqual(mock_check_isp.call_count, 3)
        self.assertEqual(mock_sleep.call_count, 2)

    @patch("autodialer.apis.check_isp.check_isp", return_value=None)
    def test_invalid_retry_parameters_return_none(self, _mock_check_isp: Any):
        self.assertIsNone(check_isp_with_retries(retries=-1, delay=1))
        self.assertIsNone(check_isp_with_retries(retries=1, delay=0))


if __name__ == "__main__":
    unittest.main()