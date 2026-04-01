import importlib
import unittest
from typing import Any
from unittest.mock import patch


vendor_api_module = importlib.import_module("autodialer.apis.utils.get_vendor_api")


class TestGetVendorApi(unittest.TestCase):
    def setUp(self) -> None:
        vendor_api_module._get_vendor_api_registry.cache_clear()

    @patch.object(vendor_api_module, "check_router_vendor", return_value="ASUS")
    def test_returns_asus_api_for_asus_vendor(self, _mock_vendor: Any):
        api_class = vendor_api_module.get_vendor_api()

        self.assertIsNotNone(api_class)
        self.assertEqual(api_class.__name__, "AsusAPI")

    @patch.object(vendor_api_module, "check_router_vendor", return_value="TP-Link")
    def test_returns_tplink_api_for_tplink_vendor(self, _mock_vendor: Any):
        api_class = vendor_api_module.get_vendor_api()

        self.assertIsNotNone(api_class)
        self.assertEqual(api_class.__name__, "TPLinkAPI")

    @patch.object(vendor_api_module, "check_router_vendor", return_value="ASUS AiMesh")
    def test_returns_asus_api_for_supported_alias(self, _mock_vendor: Any):
        api_class = vendor_api_module.get_vendor_api()

        self.assertIsNotNone(api_class)
        self.assertEqual(api_class.__name__, "AsusAPI")

    @patch.object(vendor_api_module, "check_router_vendor", return_value="Unknown")
    def test_returns_none_for_unknown_vendor(self, _mock_vendor: Any):
        api_class = vendor_api_module.get_vendor_api()

        self.assertIsNone(api_class)
