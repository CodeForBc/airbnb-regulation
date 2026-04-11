from django.test import TestCase
from listings.harvester_app.harvester.spiders.listings_spider import extract_registration_numbers

class SpiderUtilsTest(TestCase):
    """
    Unit tests for utility functions used within the Scrapy spiders,
    specifically focusing on data extraction and string parsing.
    """

    def test_extract_registration_numbers_with_space_after_hash(self):
        """Tests the specific fix for spaces between the '#' and the numeric ID."""
        text = "Municipal registration number: # 11-11111<br />Provincial registration number: H011111001"
        result = extract_registration_numbers(text)
        self.assertEqual(result, "11-11111;H011111001")

    def test_extract_registration_numbers_no_space(self):
        """Tests the standard format without extra spaces."""
        text = "Municipal registration number: #11-11111<br />Provincial registration number: H011111001"
        result = extract_registration_numbers(text)
        self.assertEqual(result, "11-11111;H011111001")

    def test_extract_registration_numbers_no_hash_symbol(self):
        """Tests cases where the hash symbol is omitted entirely."""
        text = "Municipal registration number: 11-11111"
        result = extract_registration_numbers(text)
        # Provincial should be empty
        self.assertEqual(result, "11-11111;")

    def test_extract_registration_numbers_only_provincial(self):
        """Tests cases where only the provincial number is provided."""
        text = "Provincial registration number: H011111001"
        result = extract_registration_numbers(text)
        # Municipal should be empty
        self.assertEqual(result, ";H011111001")

    def test_extract_registration_numbers_malformed_text(self):
        """Tests handling of text that does not contain registration info."""
        text = "This listing is exempt from registration."
        result = extract_registration_numbers(text)
        self.assertEqual(result, ";")

    def test_extract_registration_numbers_case_insensitivity(self):
        """Ensures the regex handles different casing for the labels."""
        text = "MUNICIPAL REGISTRATION NUMBER: 11-11111"
        result = extract_registration_numbers(text)
        self.assertEqual(result, "11-11111;")

    def test_extract_registration_numbers_with_spaced_hyphen(self):
        """Tests the format where hyphens have surrounding spaces (e.g., '26 - 162098')."""
        text = "Municipal registration number: 11 - 11111<br />Provincial registration number: H011111002"
        result = extract_registration_numbers(text)
        self.assertEqual(result, "11-11111;H011111002")

    def test_extract_registration_numbers_with_no_dot_prefix(self):
        """Tests the format where the prefix 'No.' is used before the ID."""
        text = "Municipal registration number: No. 11-11111<br />Provincial registration number: H011111003"
        result = extract_registration_numbers(text)
        self.assertEqual(result, "11-11111;H011111003")

    def test_extract_registration_numbers_with_licence_prefix(self):
        """Tests the format where the prefix 'Licence' is used before the ID."""
        text = "Municipal registration number: Licence  11-11111<br />Provincial registration number: H011111004"
        result = extract_registration_numbers(text)
        self.assertEqual(result, "11-11111;H011111004")

    def test_extract_registration_numbers_with_city_and_license_prefix(self):
        """Tests the format with city name and 'License#' prefix."""
        text = "Municipal registration number: Vancouver License# 11-11111<br />Provincial registration number: H011111005"
        result = extract_registration_numbers(text)
        self.assertEqual(result, "11-11111;H011111005")

    def test_extract_registration_numbers_with_hash_and_space(self):
        """Tests the format with '#' followed by a space."""
        text = "Municipal registration number: # 11-11111<br />Provincial registration number: H011111006"
        result = extract_registration_numbers(text)
        self.assertEqual(result, "11-11111;H011111006")