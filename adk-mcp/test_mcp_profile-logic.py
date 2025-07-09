import unittest
import re

# Import the function to be tested
from mcp_profile import _get_secret

class TestGetSecretImplementation(unittest.TestCase):
    """
    Unit tests for the _get_secret function.
    These tests are specifically designed to validate the logic as implemented,
    without making assumptions about intended behavior.
    """

    def test_long_name_is_truncated_to_first_four(self):
        """Tests that a long name is truncated to its first 4 characters and padded."""
        result = _get_secret("ABCDEFGHIJKLMNOP")
        self.assertEqual(len(result), 8)
        self.assertTrue(result.startswith("ABCD"))
        self.assertTrue(re.match(r'ABCD\d{4}', result))

    def test_short_name_is_padded(self):
        """Tests that a name shorter than 4 chars is used as-is and padded."""
        result = _get_secret("AB")
        self.assertEqual(len(result), 8)
        self.assertTrue(result.startswith("AB"))
        self.assertTrue(re.match(r'AB\d{6}', result))

    def test_none_input_becomes_none_string(self):
        """Tests that a None input is converted to the string 'NONE' and processed."""
        result = _get_secret(None)
        self.assertEqual(len(result), 8)
        self.assertTrue(result.startswith("NONE"))
        self.assertTrue(re.match(r'NONE\d{4}', result))

    def test_empty_string_defaults_to_null(self):
        """Tests that an empty string input defaults to 'NULL'."""
        result = _get_secret("")
        self.assertEqual(len(result), 8)
        self.assertTrue(result.startswith("NULL"))
        self.assertTrue(re.match(r'NULL\d{4}', result))

    def test_integer_input_is_converted_and_processed(self):
        """Tests that a number is converted to a string and truncated."""
        result = _get_secret(1234567890)
        self.assertEqual(len(result), 8)
        self.assertTrue(result.startswith("1234"))
        self.assertTrue(re.match(r'1234\d{4}', result))

    def test_sanitization_removes_special_chars_and_uppercases(self):
        """Tests that special characters are removed before truncation."""
        result = _get_secret("!!ab-cd-ef-gh-ij-kl!!") # Sanitizes to ABCDEFGHIJKL
        self.assertEqual(len(result), 8)
        self.assertTrue(result.startswith("ABCD"))
        self.assertTrue(re.match(r'ABCD\d{4}', result))

    def test_sanitization_that_results_in_empty_string(self):
        """Tests that a string with only special chars defaults to 'NULL'."""
        result = _get_secret("!@#$%^&*()") # Sanitizes to empty string
        self.assertEqual(len(result), 8)
        self.assertTrue(result.startswith("NULL"))
        self.assertTrue(re.match(r'NULL\d{4}', result))

    def test_name_of_exactly_4_chars(self):
        """Tests a name that results in a base of exactly 4 characters."""
        result = _get_secret("WXYZ")
        self.assertEqual(len(result), 8)
        self.assertTrue(result.startswith("WXYZ"))
        self.assertTrue(re.match(r'WXYZ\d{4}', result))

if __name__ == '__main__':
    unittest.main()
