import json
import base64
import re
from typing import List, Dict, Any

import scrapy
from scrapy import Request

from listings.harvester_app.harvester.items import ExpandedAirBnBListingItem
from scrapy.http import Response
from urllib.parse import quote
from listings.harvester_app.harvester.spiders.airbnb_url_builder import AirBnbURLBuilder
from listings.harvester_app.harvester.spiders.coordinates_builder import AirbnbCoordinatesBuilder
from listings.harvester_app.harvester.spiders.constants import Cities


def extract_registration_numbers(text: str) -> str:
    """
    Extract Municipal and Provincial registration numbers from text.

    Args:
        text: Text containing registration information

    Returns:
        String in format "municipal;provincial" where empty values are represented as empty strings
    """
    # Pattern to extract Municipal registration number
    municipal_pattern = r'Municipal registration number:\s*(\d+)'

    # Pattern to extract Provincial registration number
    provincial_pattern = r'Provincial registration number:\s*([A-Z0-9]+)'

    # Search for both patterns
    municipal_match = re.search(municipal_pattern, text, re.IGNORECASE)
    provincial_match = re.search(provincial_pattern, text, re.IGNORECASE)

    # Extract values or use empty string if not found
    municipal = municipal_match.group(1) if municipal_match else ""
    provincial = provincial_match.group(1) if provincial_match else ""

    # Format as requested
    return f"{municipal};{provincial}"

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

    # Instance of CoordinatesBuilder to generate the coordinates for a city.
    COORDINATES_BUILDER = AirbnbCoordinatesBuilder()

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
        Generate coordinates dynamically using AirbnbCoordinatesBuilder for Vancouver.

        Returns:
            List[Dict[str, float]]: A list of coordinate dictionaries, where each dictionary
            contains 'ne_lat', 'ne_lng', 'sw_lat', and 'sw_lng' keys with float values.
            Returns an empty list in case of an error.
        """
        try:
            return ListingsSpider.COORDINATES_BUILDER.build_coordinates(Cities.VANCOUVER)
        except Exception as e:
            print(f"Unexpected error: {e}")
            return []  # Catch-all for any other issues

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
        print("done 1")
        results = self._parse_listings_json(script_json)
        print("done 2")

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
        results_one, results_two = results
        for i in range(len(results_one)):
            try:
                # Check if this is a split listing
                if results_one[i].get('__typename') == 'ExploreSplitStaysListingItem':
                    # Handle split listings
                    async for request in self._process_split_listing(results_one[i]):
                        yield request
                else:
                    # Handle regular listings
                    listing_data = self._extract_listing_data(
                        (results_one[i], results_two[i] if i < len(results_two) else None))
                    print("testing if we have data", listing_data)
                    if listing_data:
                        yield self._create_listing_request(listing_data)
            except Exception as e:
                print(f"Exception processing listing: {e}")

    def _extract_split_listing_data(self, stay: Dict[str, Any], split_listing_item: Dict[str, Any]) -> Dict[
                                                                                                           str, Any] | None:
        """
        Extract relevant data from a single split listing stay.

        Args:
            stay (Dict[str, Any]): The individual stay within the split listing.
            split_listing_item (Dict[str, Any]): The parent split listing item containing pricing info.

        Returns:
            Dict[str, Any]: A dictionary of extracted listing data, or None if the listing
            should be skipped.
        """
        listing_id = stay.get("id")

        if not listing_id:
            print(f"Missing listing ID in split stay.\nStay: {json.dumps(stay)}")
            return None

        # For split listings, we need to handle the pricing differently
        # The pricing info is in the parent split_listing_item
        pricing_info = split_listing_item.get('structuredStayDisplayPrice', {})

        # Extract check-in and check-out dates from listingParamOverrides
        param_overrides = stay.get('listingParamOverrides', {})
        checkin_date = param_overrides.get('checkin', '')
        checkout_date = param_overrides.get('checkout', '')

        return {
            "airbnb_listing_id": listing_id,
            "title": stay.get("title", ""),
            "name": stay.get("name", ""),
            "latitude": stay.get("lat", ""),
            "longitude": stay.get("lng", ""),
            "room_type": stay.get("pdpSubtitle", ""),
            # Note: Host information is not available in split listings structure
            "user_id": "",
            "host_name": "",
            "title_text": "",
            "profile_picture_url": "",
            "thumbnail_url": "",
            "is_verified": False,
            "is_superhost": False,
            "rating_count": 0,
            "rating_average": 0.0,
            "time_as_host_years": "",
            "time_as_host_months": ""
        }

    async def _process_split_listing(self, split_listing_item: Dict[str, Any]):
        """
        Process a split listing item which contains multiple individual listings.

        Args:
            split_listing_item (Dict[str, Any]): The split listing item containing multiple stays.

        Yields:
            Request: A request object for each individual listing in the split stay.
        """
        split_stays = split_listing_item.get('splitStaysListings', [])

        for stay in split_stays:
            try:
                listing_data = self._extract_split_listing_data(stay, split_listing_item)
                if listing_data:
                    yield self._create_listing_request(listing_data)
            except Exception as e:
                print(f"Exception processing split stay: {e}")

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
        result_one, result_two = result

        # The primary listing data is in result_one
        listing_info = result_one.get('demandStayListing', {})
        listing_id_encoded = listing_info.get("id")

        if not listing_id_encoded:
            print(f"Missing listing ID.\nResults: {json.dumps(result_one)}")
            return None

        # Decode the base64 ID to get the numeric part
        try:
            decoded_id = base64.b64decode(listing_id_encoded).decode('utf-8')
            listing_id = decoded_id.split(':')[-1]
        except (TypeError, IndexError):
            print(f"Could not decode or parse listing ID: {listing_id_encoded}")
            return None

        return {
            "airbnb_listing_id": listing_id,
            "title": result_one.get("title", ""),
            "name": self._safe_get(listing_info, "description", "name", "localizedStringWithTranslationPreference",
                                   default=""),
            "latitude": self._safe_get(listing_info, "location", "coordinate", "latitude", default=""),
            "longitude": self._safe_get(listing_info, "location", "coordinate", "longitude", default=""),
            "room_type": result_one.get("roomTypeCategory", ""),  # Using title as room_type as per analysis
            "user_id": result_one.get("passportData", {}).get("userId", ""),
            "host_name": result_one.get("passportData", {}).get("name", ""),
            "titleText": result_one.get("passportData", {}).get("titleText", ""),
            "profile_picture_url": result_one.get("passportData", {}).get("profilePictureUrl", ""),  # profilePictureUrl
            "thumbnail_url": result_one.get("passportData", {}).get("thumbnailUrl", ""),  # thumbnailUrl
            "is_verified": result_one.get("passportData", {}).get("isVerified", False),
            "is_superhost": result_one.get("passportData", {}).get("isSuperhost", False),
            "rating_count": result_one.get("passportData", {}).get("ratingCount", 0),
            "rating_average": result_one.get("passportData", {}).get("ratingAverage", 0.0),
            "time_as_host_years": result_one.get("passportData", {}).get("timeAsHost", {}).get("years", ""),
            "time_as_host_months": result_one.get("passportData", {}).get("timeAsHost", {}).get("months", "")

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
            room_type=airbnb_params.get('room_type'),
            # Host Information
            user_id=airbnb_params.get("user_id"),
            host_name=airbnb_params.get("host_name"),
            title_text=airbnb_params.get("titleText"),
            profile_picture_url=airbnb_params.get("profile_picture_url"),
            thumbnail_url=airbnb_params.get("thumbnail_url"),
            is_verified=airbnb_params.get("is_verified"),
            is_superhost=airbnb_params.get("is_superhost"),
            rating_count=airbnb_params.get("rating_count"),
            rating_average=airbnb_params.get("rating_average"),
            time_as_host_years=airbnb_params.get("time_as_host_years"),
            time_as_host_months=airbnb_params.get("time_as_host_months"),
        )
        try:
            script_tag_json = json.loads(response.text)
            ListingsSpider._parse_capacity_and_location(script_tag_json, listing_item)
            ListingsSpider._parse_listings_number(script_tag_json, listing_item)
            ListingsSpider._parse_host_id(script_tag_json, listing_item)
        except Exception as e:
            print(e)
        finally:
            yield listing_item

    @staticmethod
    def _parse_host_id(self, script_tag_json, listing_item) -> ExpandedAirBnBListingItem:
        """
        Handle the response from the listing detail page and extract host information.

        Args:
            response (Response): The response object from the listing detail page request.

        Returns:
            ExpandedAirBnBListingItem: The scraped listing item with host information.
        """

        sections = script_tag_json.get('data', {}).get('presentation', {}).get('stayProductDetailPage', {}).get('sections',
                                                                                                            {}).get(
            'sections', [])

        host_info = {}
        for section in sections:
            if section.get('sectionId') == 'MEET_YOUR_HOST':
                card_data = section.get('section', {}).get('cardData', {})
                host_info = {
                    'user_id': card_data.get('userId'),
                    'host_name': card_data.get('name'),
                    'profile_picture_url': card_data.get('profilePictureUrl'),
                    'is_superhost': card_data.get('isSuperhost'),
                }
                break
        listing_item['user_id'] = host_info['user_id']
        listing_item['host_name'] = host_info['host_name']
        listing_item['profile_picture_url'] = host_info['profile_picture_url']
        listing_item['is_superhost'] = host_info['is_superhost']
        return listing_item

    @staticmethod
    def _parse_capacity_and_location(script_tag_json, listing_item):
        """
        Extract the room capacity and location (City) of the listing from the provided JSON data.
        """
        location = ""
        person_capacity = ""
        try:
            # Look for location and capacity in the sidebar and house rules
            sidebar = ListingsSpider._safe_get(script_tag_json, "data", "presentation", "stayProductDetailPage",
                                               "sidebar", "bookItSidebar", default={})
            person_capacity = sidebar.get("maxGuestCapacity", "")

            sections = ListingsSpider._parse_listing_json(script_tag_json)
            for section in sections:
                if ListingsSpider._safe_get(section, "sectionId") == "LOCATION_DEFAULT":
                    location = ListingsSpider._safe_get(section, "section", "subtitle", default="")
                # Fallback for person_capacity from house rules if not in sidebar
                if not person_capacity and ListingsSpider._safe_get(section, "sectionId") == "POLICIES_DEFAULT":
                    house_rules = ListingsSpider._safe_get(section, "section", "houseRules", default=[])
                    for rule in house_rules:
                        if "guests maximum" in rule.get("title", ""):
                            person_capacity = rule.get("title").split(" ")[0]

        except Exception as e:
            print(e)
        finally:
            listing_item['location'] = location
            listing_item['person_capacity'] = person_capacity

    @staticmethod
    def _parse_listings_number(data: str, listing_item) -> Dict[str, str]:
        """
        Extract title and registration numbers from Airbnb listing JSON.

        Args:
            json_file_path: Path to the JSON file

        Returns:
            Dictionary with extracted data
        """
        try:


            # Initialize result dictionary
            result = {
                'title': '',
                'registration_numbers': '',
                'municipal_number': '',
                'provincial_number': '',
                'raw_registration_text': ''
            }

            # Navigate through the JSON structure to find the title
            try:
                title_section = data['data']['presentation']['stayProductDetailPage']['sections']['sections']

                # Find the title section
                for section in title_section:
                    if section.get('sectionId') == 'TITLE_DEFAULT':
                        result['title'] = section['section']['title']
                        break
            except (KeyError, TypeError) as e:
                print(f"Warning: Could not extract title - {e}")

            # Find registration details in the description modal
            try:
                for section in title_section:
                    if section.get('sectionId') == 'DESCRIPTION_MODAL':
                        items = section['section']['items']

                        # Look for registration details section
                        for item in items:
                            if item.get('title') == 'Registration details':
                                html_text = item['html']['htmlText']
                                result['raw_registration_text'] = html_text

                                # Extract registration numbers
                                registration_numbers = extract_registration_numbers(html_text)
                                result['registration_numbers'] = registration_numbers

                                # Split for individual numbers
                                municipal, provincial = registration_numbers.split(';')
                                result['municipal_number'] = municipal
                                result['provincial_number'] = provincial
                                break
                        break
            except (KeyError, TypeError) as e:
                print(f"Warning: Could not extract registration numbers - {e}")

            finally:
                listing_item["beds"] = ""
                listing_item["baths_text"] = ""
                listing_item["registration_number"] = result['registration_numbers']
        except json.JSONDecodeError as e:
            print(f"Error: Invalid JSON format - {e}")
            return {}
        except Exception as e:
            print(f"Error: Unexpected error - {e}")
            return {}
    #
    # @staticmethod
    # def _parse_listings_number(script_tag_json, listing_item):
    #     """
    #     Extract the registration number, number of beds, and number of baths from the provided JSON data.
    #     """
    #     registration_number = ""
    #     number_of_beds = ""
    #     number_of_baths = ""
    #
    #     try:
    #         sections = ListingsSpider._parse_listing_json(script_tag_json)
    #         print("sections_dump:", json.dumps(sections))
    #         for section in sections:
    #             # Get registration number from description modal
    #             if section.get("sectionId") == "DESCRIPTION_MODAL":
    #                 items = section.get("section", {}).get("items", [])
    #                 print("Inside description sections")
    #                 for item in items:
    #                     print("title: ", item.get("title", ""))
    #                     if "Registration" in item.get("title", ""):
    #                         html_text = item.get("html", {}).get("htmlText", "")
    #
    #                         # Extract both registration numbers
    #                         municipal_number = ""
    #                         provincial_number = ""
    #
    #                         if "Municipal registration number" in html_text:
    #                             municipal_number = html_text.split("Municipal registration number: ")[-1].split("<br")[
    #                                 0].strip()
    #
    #                         if "Provincial registration number" in html_text:
    #                             provincial_number = \
    #                             html_text.split("Provincial registration number: ")[-1].split("<br")[0].strip()
    #
    #                         # Combine numbers with colon separator
    #                         if municipal_number and provincial_number:
    #                             registration_number = f"{municipal_number}:{provincial_number}"
    #                         elif municipal_number:
    #                             registration_number = municipal_number
    #                         elif provincial_number:
    #                             registration_number = provincial_number
    #
    #             # Get bed and bath info. This is fragile and depends on the text.
    #             if section.get("sectionId") == "HIGHLIGHTS_DEFAULT":
    #                 highlights = section.get("section", {}).get("highlights", [])
    #                 for highlight in highlights:
    #                     title = highlight.get("title", "")
    #                     if "bed" in title.lower():
    #                         number_of_beds = title
    #                     if "bath" in title.lower():
    #                         number_of_baths = title
    #     except Exception as e:
    #         print("Exception occurred:", e)
    #     finally:
    #         listing_item["beds"] = number_of_beds
    #         listing_item["baths_text"] = number_of_baths
    #         listing_item["registration_number"] = registration_number


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
        except (KeyError, TypeError, IndexError):
            # print("data", data, keys) # This can be very verbose, uncomment for debugging
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
        return (
            ListingsSpider._safe_get(
                listings_json,
                "niobeClientData", 0, 1, "data", "presentation", "staysSearch",
                "results", "searchResults",
                default=[]
            ),
            ListingsSpider._safe_get(
                listings_json,
                "niobeClientData", 0, 1, "data", "presentation", "staysSearch",
                "mapResults", "staysInViewport",
                default=[]
            )
        )

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
                                        "sections", "metadata", default={})

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
