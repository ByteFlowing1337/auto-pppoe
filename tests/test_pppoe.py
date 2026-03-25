import unittest

from autodialer.pppoe import is_target_asn


class TestIsTargetAsn(unittest.TestCase):
    def test_matches_with_as_prefix(self):
        self.assertTrue(is_target_asn("AS9929 Chunghwa Telecom", "AS9929"))

    def test_matches_without_as_prefix(self):
        self.assertTrue(is_target_asn("AS9929 Chunghwa Telecom", "9929"))

    def test_matches_with_whitespace_and_case(self):
        self.assertTrue(is_target_asn("as1234 Example ISP", "  As1234 "))

    def test_returns_false_for_non_matching_asn(self):
        self.assertFalse(is_target_asn("AS4766 ISP", "AS9929"))

    def test_returns_false_for_missing_or_invalid_inputs(self):
        self.assertFalse(is_target_asn(None, "AS9929"))
        self.assertFalse(is_target_asn("AS9929 ISP", None))
        self.assertFalse(is_target_asn("", "AS9929"))
        self.assertFalse(is_target_asn("AS9929 ISP", ""))


if __name__ == "__main__":
    unittest.main()