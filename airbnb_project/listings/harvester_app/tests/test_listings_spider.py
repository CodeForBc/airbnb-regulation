import unittest
import requests
from unittest.mock import patch, Mock
from scrapy.http import Request, TextResponse
from listings.harvester_app.harvester.spiders.listings_spider import ListingsSpider
from listings.harvester_app.harvester.harvester_settings import get_harvester_settings


class TestListingsSpider(unittest.TestCase):

    def setUp(self):
        # Initialize a new ListingsSpider instance before each test
        self.spider = ListingsSpider()
        self.spider.settings = get_harvester_settings()

    def test_generate_requests(self):
        """
        Test that _generate_requests creates the correct number of requests
        based on the provided coordinates and URL templates.
        """
        coordinates = [{"ne_lat": 1.0, "ne_lng": 2.0, "sw_lat": 3.0, "sw_lng": 4.0}]
        requests = self.spider._generate_requests(coordinates)
        self.assertTrue(len(requests) > 0 and isinstance(requests[0], Request))

    def test_extract_script_json(self):
        """
        Test that _extract_script_json correctly extracts and parses JSON data
        from the script tag in the HTML response.
        """
        html_content = '<html><body><script id="data-deferred-state-0">{"key": "value"}</script></body></html>'
        response = TextResponse(url="http://example.com", body=html_content, encoding='utf-8')
        script_json = self.spider._extract_script_json(response)
        self.assertEqual(script_json, {"key": "value"})

    def test_extract_listing_data(self):
        """
        Test that _extract_listing_data correctly extracts relevant data
        from a single listing result dictionary.
        """
        result = {
            "listing": {
                "id": "456",
                "title": "Test Listing",
                "name": "Test Name",
                "coordinate": {"latitude": 1.0, "longitude": 2.0},
                "roomTypeCategory": "Entire home"
            }
        }
        listing_data = self.spider._extract_listing_data(result)
        self.assertEqual(listing_data["airbnb_listing_id"], "456")
        self.assertEqual(listing_data["title"], "Test Listing")

    @patch('requests.get')
    def test_create_listing_request(self, mock_get):
        """
        Test that _create_listing_request correctly creates a Request object
        for a listing's details page with the right URL and headers.
        """
        # Setup mock response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_get.return_value = mock_response

        listing_data = {
            "airbnb_listing_id": "789",
            "title": "Test Listing",
            "name": "Test Name",
            "latitude": 1.0,
            "longitude": 2.0,
            "room_type": "Entire home"
        }
        request = self.spider._create_listing_request(listing_data)
        self.assertIsInstance(request, Request)
        response = requests.get(request.url, headers={'X-Airbnb-Api_Key': request.headers['X-Airbnb-Api-Key']})

        # Check if the status code is 200`
        self.assertEqual(response.status_code, 200)

    @patch.object(ListingsSpider, '_parse_capacity_and_location')
    @patch.object(ListingsSpider, '_parse_listings_number')
    def test_handle_listing(self, mock_parse_listings, mock_parse_capacity):
        """
        Test that handle_listing correctly processes a listing's details page.
        We mock the internal parsing methods and check if they're called.
        """
        meta = {
            "airbnb_listing_id": "123",
            "title": "Test",
            "name": "Test Name",
            "latitude": 1.0,
            "longitude": 2.0,
            "room_type": "Entire home"
        }
        sample_request = Request(
            url="http://example.com",
            meta={'airbnb_params': meta}
        )
        response = TextResponse(url="http://example.com", body=b'{"key": "value"}', request=sample_request)

        response.meta['airbnb_params'] = {
            "airbnb_listing_id": "123",
            "title": "Test",
            "name": "Test Name",
            "latitude": 1.0,
            "longitude": 2.0,
            "room_type": "Entire home"
        }

        generator = self.spider.handle_listing(response)
        item = next(generator)

        self.assertEqual(item['airbnb_listing_id'], "123")
        self.assertEqual(item['title'], "Test")
        mock_parse_capacity.assert_called_once()
        mock_parse_listings.assert_called_once()

    def test_parse_capacity_and_location(self):
        """
        Test that _parse_capacity_and_location correctly extracts capacity and location
        information from the JSON data of a listing's details page.
        """
        script_tag_json = {
            "data": {
                "presentation": {
                    "stayProductDetailPage": {
                        "sections": {
                            "metadata": {
                                "sharingConfig": {
                                    "location": "Test City",
                                    "personCapacity": "4"
                                }
                            }
                        }
                    }
                }
            }
        }
        listing_item = {}
        ListingsSpider._parse_capacity_and_location(script_tag_json, listing_item)
        self.assertEqual(listing_item['location'], "Test City")
        self.assertEqual(listing_item['person_capacity'], "4")

    def test_parse_listings_number(self):
        """
        Test that _parse_listings_number correctly extracts registration number,
        number of beds, and number of baths from the JSON data of a listing's details page.
        """
        script_tag_json = {
            "data": {
                "presentation": {
                    "stayProductDetailPage": {
                        "sections": {
                            "sections": [
                                {
                                    "sectionComponentType": "PDP_DESCRIPTION_MODAL",
                                    "section": {
                                        "items": [
                                            {
                                                "title": "Registration number",
                                                "html": {"htmlText": "123456"}
                                            }
                                        ]
                                    }
                                },
                                {
                                    "sectionComponentType": "AVAILABILITY_CALENDAR_DEFAULT",
                                    "section": {
                                        "descriptionItems": [
                                            {"title": "2 beds"},
                                            {"title": "1 bath"}
                                        ]
                                    }
                                }
                            ]
                        }
                    }
                }
            }
        }
        listing_item = {}
        ListingsSpider._parse_listings_number(script_tag_json, listing_item)
        self.assertEqual(listing_item['registration_number'], "123456")
        self.assertEqual(listing_item['beds'], "2 beds")
        self.assertEqual(listing_item['baths_text'], "1 bath")


if __name__ == '__main__':
    unittest.main()
