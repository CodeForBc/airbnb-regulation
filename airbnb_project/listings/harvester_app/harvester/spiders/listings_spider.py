import csv
import json
import base64
import os
from typing import List, Dict, Any

import scrapy
from scrapy import Request
from scrapy.crawler import CrawlerProcess

from listings.harvester_app.harvester.items import ExpandedAirBnBListingItem
from scrapy.http import Response
from urllib.parse import quote
from listings.harvester_app.harvester.spiders.airbnb_url_builder import AirBnbURLBuilder


def base64_encode_string(input_string):
    """
    Encode the input string `input_string` into bytes, then encode it in base64, and decode it back to a UTF-8 string.

    :param input_string: The input string to be encoded.
    :return: The base64 encoded string.
    """
    return base64.b64encode(input_string.encode('utf-8')).decode('utf-8')


def combine_and_url_encode(base_string, url_string):
    """
    Encode the second string `url_string` using URL encoding, replace spaces with plus signs, and return the combined format.

    :param base_string: The first part of the string to be combined.
    :param url_string: The string to be URL encoded and combined.
    :return: A formatted string combining `base_string` and the encoded version of `url_string`.
    """
    encoded_t = quote(url_string, safe='').replace('%20', '+').replace('(', '%28').replace(')', '%29')
    return f"{base_string}:{encoded_t}"


class ListingsSpider(scrapy.Spider):
    """
    Spider for scraping Airbnb listings.
    """
    # Name of the spider, used by Scrapy to identify this spider
    name = "listings_spider"

    # List of allowed domains for the spider to crawl
    allowed_domains = ['airbnb.ca']

    # List to store pagination cursors for navigating through result pages
    next_page_cursors: [str] = None

    # Counter to keep track of the total number of listings scraped
    total_listings = 0

    # Instance of AirBnbURLBuilder to generate URLs for different search parameters
    URL_BUILDER = AirBnbURLBuilder()

    def start_requests(self) -> List[scrapy.FormRequest]:
        """
        Generate initial requests for scraping Airbnb listings using coordinates from a JSON file.

        This method orchestrates the process of loading already scraped listings,
        loading coordinates, and generating requests based on those coordinates.

        Returns:
            List[scrapy.FormRequest]: A list of FormRequest objects for initial scraping.
        """
        coordinates = self._load_coordinates()
        return self._generate_requests(coordinates)

    def _load_coordinates(self) -> List[Dict[str, float]]:
        """
        Read coordinates from a JSON file.

        This method attempts to read and parse a 'coordinates.json' file,
        which should contain a list of coordinate dictionaries.

        Returns:
            List[Dict[str, float]]: A list of coordinate dictionaries, where each dictionary
            contains 'ne_lat', 'ne_lng', 'sw_lat', and 'sw_lng' keys with float values.
            Returns an empty list if the file is not found or cannot be parsed.

        Raises:
            FileNotFoundError: If the 'coordinates.json' file is not found.
            json.JSONDecodeError: If there's an error decoding the JSON in the file.
        """
        try:
            # Get the absolute path to the current script (listings_spider.py)
            current_directory = os.path.dirname(os.path.abspath(__file__))
            # Construct the absolute path to coordinates.json
            coordinates_file_path = os.path.join(current_directory, 'coordinates.json')
            with open(coordinates_file_path, 'r') as file:
                return json.load(file)
        except FileNotFoundError:
            print("Coordinates file not found")
            return []
        except json.JSONDecodeError:
            print("Error decoding JSON in coordinates file")
            return []
        except Exception:
            print("Unknown error occurred while reading the coordinates file")
            return []

    def _generate_requests(self, coordinates: List[Dict[str, float]]) -> List[scrapy.FormRequest]:
        """
        Construct and return a list of initial Scrapy requests using template URLs and coordinates.

        This method creates FormRequest objects for each combination of URL template
        (obtained from URL_BUILDER) and coordinate set.

        Args:
            coordinates (List[Dict[str, float]]): A list of coordinate dictionaries, where each
                dictionary contains 'ne_lat', 'ne_lng', 'sw_lat', and 'sw_lng' keys with float values.

        Returns:
            List[scrapy.FormRequest]: A list of FormRequest objects, each initialized with
            a URL formatted with coordinates and zoom level.
        """
        if not coordinates:
            return []

        urls = self.URL_BUILDER.get_urls()
        requests = []
        zoom_level = self.settings.get('ZOOM_LEVEL')
        for url in urls:
            for cord in coordinates:
                formatted_url = url.format(
                    cord["ne_lat"], cord["ne_lng"], cord["sw_lat"], cord["sw_lng"],
                    zoom_level, zoom_level
                )
                requests.append(scrapy.FormRequest(formatted_url))
        print('Hitting the below URLs in this run....')
        print(requests)
        return requests

    async def parse(self, response: Response, **kwargs) -> None:
        """
        Parse method for extracting listings from the Airbnb search results page.

        This method orchestrates the parsing process by extracting JSON data from the script tag,
        processing individual listings, and handling pagination.

        Args:
            response (Response): The response object from the request.
            **kwargs: Additional keyword arguments.

        Yields:
            Request: Requests for individual listing detail pages.
            Request: Request for the next page of search results, if available.
        """
        script_json = self._extract_script_json(response)
        results = self._parse_listings_json(script_json)

        if self.next_page_cursors is None:
            self.next_page_cursors = self._get_cursors(script_json)

        async for request in self._process_listings(results):
            yield request

        async for request in self._handle_pagination(response):
            yield request

    def _extract_script_json(self, response: Response) -> Dict[str, Any]:
        """
        Extract JSON data from the script tag in the response.

        Args:
            response (Response): The response object from the request.

        Returns:
            Dict[str, Any]: The parsed JSON data from the script tag.
        """
        script_tag_name = self.settings.get('AIRBNB_SCRIPT_TAG')
        script_tag = response.css(f'script#{script_tag_name}')
        script_inner_text = script_tag.css('script::text').get()
        return json.loads(script_inner_text)

    async def _process_listings(self, results: List[Dict[str, Any]]):
        """
        Process each listing in the results.

        This method iterates through the results, extracts data for each listing,
        and yields a request for each listing's detail page.

        Args:
            results (List[Dict[str, Any]]): The list of listing results to process.

        Yields:
            Request: A request object for each listing's details page.
        """
        for result in results:
            try:
                listing_data = self._extract_listing_data(result)
                if listing_data:
                    yield self._create_listing_request(listing_data)
            except Exception as e:
                print(f"Exception processing listing: {e}")

    def _extract_listing_data(self, result: Dict[str, Any]) -> Dict[str, Any] | None:
        """
        Extract relevant data from a single listing result.

        This method extracts key information from the listing dictionary and checks
        if the listing has already been scraped.

        Args:
            result (Dict[str, Any]): The dictionary containing listing information.

        Returns:
            Dict[str, Any]: A dictionary of extracted listing data, or None if the listing
            should be skipped.
        """
        listing = result.get("listing", {})
        listing_id: str = listing.get("id")

        if not listing_id:
            print(f"Missing listing ID.\nResults: {json.dumps(result)}")

            return None

        return {
            "airbnb_listing_id": listing_id,
            "title": listing.get("title", ""),
            "name": listing.get("name", ""),
            "latitude": listing.get("coordinate", {}).get("latitude", ""),
            "longitude": listing.get("coordinate", {}).get("longitude", ""),
            "room_type": listing.get("roomTypeCategory", "")
        }

    def _create_listing_request(self, listing_data: Dict[str, Any]) -> Request:
        """
        Create a request for the listing's details page.

        Args:
            listing_data (Dict[str, Any]): The extracted data for a single listing.

        Returns:
            Request: A request object for the listing's details page.
        """
        airbnb_api_url = self.settings.get('AIRBNB_LISTING_API_URL')
        airbnb_api_key = self.settings.get('AIRBNB_PUBLIC_API_KEY')
        page_url = airbnb_api_url.format(
            base64_encode_string(combine_and_url_encode("StayListing", listing_data["airbnb_listing_id"])))
        return Request(
            url=page_url,
            callback=self.handle_listing,
            headers={'X-Airbnb-Api-Key': airbnb_api_key},
            meta={'airbnb_params': listing_data}
        )

    async def _handle_pagination(self, response: Response):
        """
        Handle pagination for the next page of results.

        This method checks if there are more pages to scrape and yields a request
        for the next page if available.

        Args:
            response (Response): The response object from the current request.

        Yields:
            Request: A request object for the next page of search results, if available.
        """
        if self.next_page_cursors:
            cursor_id = self.next_page_cursors.pop()
            next_url = f'{response.url}&cursor={cursor_id}'
            yield response.follow(next_url, callback=self.parse)

    @staticmethod
    def handle_listing(response: Response):
        """
        Parse method for extracting details from an Airbnb listing page.

        Args:
            response (Response): The response object from the request.

         Yields:
            ExpandedAirBnBListingItem: An ExpandedAirBnBListingItem object containing details of an Airbnb listing.
        """
        airbnb_params = response.meta.get('airbnb_params', {})
        listing_item = ExpandedAirBnBListingItem(
            airbnb_listing_id=airbnb_params.get('airbnb_listing_id'),
            title=airbnb_params.get('title'),
            name=airbnb_params.get('name'),
            latitude=airbnb_params.get('latitude'),
            longitude=airbnb_params.get('longitude'),
            room_type=airbnb_params.get('room_type')
        )
        try:
            script_tag_json = json.loads(response.text)
            ListingsSpider._parse_capacity_and_location(script_tag_json, listing_item)
            ListingsSpider._parse_listings_number(script_tag_json, listing_item)
        except Exception as e:
            print(e)
        finally:
            yield listing_item

    @staticmethod
    def _parse_capacity_and_location(script_tag_json, listing_item):
        """
        Extract the room capacity and location (City) of the listing from the provided JSON data.

        Args:
            script_tag_json (dict): The JSON data extracted from the script tag containing the listing metadata.
            listing_item (dict): The dictionary representing a single listing, where parsed data will be stored.

        Returns:
            None: This method modifies the `listing_item` dictionary in place, adding 'location' and 'person_capacity'.
        """
        location = ""
        person_capacity = ""
        try:
            metadata = ListingsSpider._get_metadata_from_json(script_tag_json)
            if metadata is not None:
                sharing_config = metadata.get("sharingConfig", {})
                location = sharing_config.get("location", "")
                person_capacity = sharing_config.get("personCapacity", "")
        except Exception as e:
            print(e)
        finally:
            listing_item['location'] = location
            listing_item['person_capacity'] = person_capacity

    @staticmethod
    def _parse_listings_number(script_tag_json, listing_item):
        """
        Extract the registration number, number of beds, and number of baths from the provided JSON data.

        Args:
            script_tag_json (dict): The JSON data extracted from the script tag containing the listing details.
            listing_item (dict): The dictionary representing a single listing, where parsed data will be stored.

        Returns:
            None: This method modifies the `listing_item` dictionary in place, adding 'registration_number', 'beds', and 'baths_text'.
        """
        registration_number = ""
        number_of_beds = ""
        number_of_baths = ""
        try:
            sections = ListingsSpider._parse_listing_json(script_tag_json)
            for section in sections:
                if section.get("sectionComponentType") == "PDP_DESCRIPTION_MODAL":
                    items = section.get("section", {}).get("items", [])
                    for item in items:
                        if item.get("title") == "Registration number":
                            registration_number = item.get("html", "").get(
                                "htmlText", "")
                            print("regis", registration_number)
                if section.get("sectionComponentType") == "AVAILABILITY_CALENDAR_DEFAULT":
                    items = section.get("section", {}).get("descriptionItems", [])
                    for item in items:
                        title = item.get("title", "")
                        if "bed" in title:
                            number_of_beds = title
                        if "bath" in title:
                            number_of_baths = title
        except Exception as e:
            print("Exception occurred:", e)
        finally:
            listing_item["beds"] = number_of_beds
            listing_item["baths_text"] = number_of_baths
            listing_item["registration_number"] = registration_number

    @staticmethod
    def _safe_get(data: dict, *keys, default=None):
        """
        Safely retrieve a nested value from a dictionary.

        Args:
            data (dict): The dictionary to retrieve the value from.
            keys (tuple): The keys to navigate the nested structure.
            default: The default value to return if the keys are not found.

        Returns:
            The value at the specified nested key or the default value.
        """
        try:
            for key in keys:
                data = data[key]
            return data
        except KeyError or TypeError:
            print("data", data, keys)
            return default

    @staticmethod
    def _parse_listings_json(listings_json):
        """
        Parse method for extracting listing information from a JSON object.

        Args:
            listings_json (dict): The JSON object containing the listings' information.s

        Returns:
            list: A list of listings extracted from the JSON object.
        """
        return ListingsSpider._safe_get(listings_json,
                                        "niobeMinimalClientData", 0, 1, "data", "presentation", "staysSearch",
                                        "results", "searchResults", default=[])

    @staticmethod
    def _parse_listing_json(listing_json):
        """
        Parse method for extracting listing details from a JSON object.

        Args:
            listing_json (dict): The JSON object containing the listing details.

        Returns:
            list: A list of listing details extracted from the JSON object.
        """
        return ListingsSpider._safe_get(listing_json, "data", "presentation",
                                        "stayProductDetailPage",
                                        "sections", "sections", default=[])

    @staticmethod
    def _get_metadata_from_json(listing_json: dict):
        return ListingsSpider._safe_get(listing_json, "data", "presentation",
                                        "stayProductDetailPage",
                                        "sections", "metadata", default=[])

    @staticmethod
    def _get_cursors(script_json):
        """
        Parse method for extracting pagination cursors from a JSON object.

        Args:
            script_json (dict): The JSON object containing the pagination information.

        Returns:
            list: A list of pagination cursors extracted from the JSON object.
        """
        return ListingsSpider._safe_get(script_json,
                                        "niobeMinimalClientData", 0, 1, "data", "presentation", "staysSearch",
                                        "results", "paginationInfo", "pageCursors", default=[])
