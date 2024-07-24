import csv
import json
import random

import scrapy
from scrapy import Request
from listings.harvester_app.harvester.items import AirBnBListingItem, ExpandedAirBnBListingItem
from scrapy.http import Response
import base64

from listings.harvester_app.harvester.spiders.airbnb_url_builder import AirBnbURLBuilder

# The tag used to identify the specific script data within the Airbnb HTML page.
SCRIPT_TAG = "data-deferred-state-0"

# API endpoint for retrieving detailed information about specific Airbnb listings.
# The URL requires an Airbnb listing ID to be inserted into the placeholder.
API_CALL = "https://www.airbnb.ca/api/v3/StaysPdpSections/08e3ad2e3d75c9bede923485718ff2e7f6efe2ca1febb5192d78c51e17e8b4ca?operationName=StaysPdpSections&locale=en-CA&currency=CAD&variables=%7B%22id%22%3A%22{}%22%2C%22pdpSectionsRequest%22%3A%7B%22adults%22%3A%221%22%2C%22layouts%22%3A%5B%22SINGLE_COLUMN%22%5D%7D%7D&extensions=%7B%22persistedQuery%22%3A%7B%22version%22%3A1%2C%22sha256Hash%22%3A%2237d7cbb631196506c3990783fe194d81432d0fbf7362c668e547bb6475e71b37%22%7D%7D"

# API key used for authentication when making API calls to Airbnb's services.
API_KEY = "d306zoyjsyarp7ifhu67rjxn52tv0t20"

# Zoom level parameter used in the map URL templates to define the zoom level of the map.
ZOOM_LEVEL = 15.4



def n(s):
    """
    Encode the input string `s` into bytes, then encode it in base64, and decode it back to a UTF-8 string.

    :param s: The input string to be encoded.
    :return: The base64 encoded string.
    """
    return base64.b64encode(s.encode('utf-8')).decode('utf-8')


from urllib.parse import quote


def t(n, t):
    """
    Encode the second string `t` using URL encoding, replace spaces with plus signs, and return the combined format.

    :param n: The first part of the string to be combined.
    :param t: The string to be URL encoded and combined.
    :return: A formatted string combining `n` and the encoded version of `t`.
    """
    encoded_t = quote(t, safe='').replace('%20', '+').replace('(', '%28').replace(')', '%29')
    return f"{n}:{encoded_t}"


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

    # Set to store IDs of listings that have already been scraped to avoid duplicates. This is a
    # temporary solution until a database is set up, which will then take care of duplicates etc
    ALREADY_SCRAPED_LISTINGS = set()

    # Instance of AirBnbURLBuilder to generate URLs for different search parameters
    URL_BUILDER = AirBnbURLBuilder()

    def start_requests(self):
        """
       Generates initial requests for scraping Airbnb listings using coordinates from a JSON file.

       This function performs the following steps:
       1. Reads already scraped Airbnb listing IDs from a CSV file and stores them in a set.
       2. Reads coordinates from a JSON file and shuffles them.
       3. Constructs and returns a list of initial Scrapy requests using template URLs and the read coordinates.

       :return: List of Scrapy FormRequest objects initialized with map coordinates for Vancouver.
        """
        file_name = self.settings.get("CSV_STORE_FILE_NAME")
        try:
            with open(
                    f"{file_name}",
                    "r",
                    encoding="utf8") as file:
                read_csv_file = csv.DictReader(file)
                for row in read_csv_file:
                    row: dict
                    ListingsSpider.ALREADY_SCRAPED_LISTINGS.add(row['airbnb_listing_id'])
        except FileNotFoundError as e:
            print(e)
        requests = []
        try:
            with open('cordinates.json', 'r') as file:
                coordinates = json.load(file)
                urls = ListingsSpider.URL_BUILDER.get_urls("july", "june", "august")
                if coordinates is not None:
                    requests = [scrapy.FormRequest(
                        url.format(cord["ne_lat"], cord["ne_lng"], cord["sw_lat"], cord["sw_lng"],
                                   ZOOM_LEVEL,
                                   ZOOM_LEVEL)) for url in urls for
                        cord in
                        coordinates]
        except FileNotFoundError:
            print("The file was not found")
        except json.JSONDecodeError:
            print("Error decoding JSON")
        return requests

    async def parse(self, response: Response, **kwargs):
        """
        Parse method for extracting listings from the Airbnb search results page.

        Args:
            response (Response): The response object from the request.

        Yields:
            Request: A request object for each listing's details page.
        """
        if response.status != 200:
            return
        script_tag = response.css(f'script#{SCRIPT_TAG}')
        script_inner_text = script_tag.css('script::text').get()
        script_json = json.loads(script_inner_text)
        results = self._parse_listings_json(script_json)
        current_url = response.url

        if ListingsSpider.next_page_cursors is None:
            ListingsSpider.next_page_cursors = self._get_cursors(script_json)

        for result in results:
            try:
                listing = result.get("listing", {})
                listing_id: str = listing.get("id")
                print("listing_id", listing_id)
                title = listing.get("title", "")
                name = listing.get("name", "")
                coordinate = listing.get("coordinate", {})
                latitude = coordinate.get("latitude", "")
                longitude = coordinate.get("longitude", "")
                room_type = listing.get("roomTypeCategory", "")
                page_url = API_CALL.format(n(t("StayListing", listing_id)))
                airbnb_params = {
                    "airbnb_listing_id": listing_id,
                    "title": title,
                    "name": name,
                    "latitude": latitude,
                    "longitude": longitude,
                    "room_type": room_type
                }

                # A second request is made to get the registration number and other information using the listing_id
                # which is scarped
                if listing_id and listing_id not in ListingsSpider.ALREADY_SCRAPED_LISTINGS:
                    yield Request(url=page_url, callback=self.handle_listing,
                                  headers={'X-Airbnb-Api-Key': API_KEY},
                                  meta={'airbnb_params': airbnb_params})
                else:
                    print("duplicate", listing_id)

            except Exception as e:
                print("error_listing", result)
                print("exception", e.args[0])

        if len(ListingsSpider.next_page_cursors) != 0:
            cursor_id = ListingsSpider.next_page_cursors.pop()
            next_url = f'{current_url}&cursor={cursor_id}'
            yield response.follow(next_url, callback=self.parse)

    @staticmethod
    def handle_listing(response):
        """
        Parse method for extracting details from an Airbnb listing page.

        Args:
            response (Response): The response object from the request.

         Yields:
            AirBnBListingItem: An AirBnBListingItem object containing details of an Airbnb listing.
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

        script_tag_json = json.loads(response.text)

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
        listing_item['location'] = location
        listing_item['person_capacity'] = person_capacity
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

        listing_item["beds"] = number_of_beds
        listing_item["baths_text"] = number_of_baths
        listing_item["registration_number"] = registration_number
        yield listing_item

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
