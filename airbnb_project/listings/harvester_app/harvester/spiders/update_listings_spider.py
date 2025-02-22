import base64
from typing import List, Dict, Any
from urllib.parse import quote

from listings.listing_models import Listing

from scrapy import FormRequest, Spider, Request
from scrapy.http import Response


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

class UpdateListingsSpider(Spider):
    """
    Spider for scraping Airbnb listings.
    """
    # Name of the spider, used by Scrapy to identify this spider
    name = 'update_listings_spider'

    allowed_domains = ['www.airbnb.com']

    def start_requests(self) -> List[Request]:
        """
        Generates inisital request for updating already scrapped lsitings.

        This method will query the db for all the unique listings in the databse and then
        update them with a new infomration

        Returns:
            List[FormRequest]: List of FormRequest objects with urls with the listing ids.
        """
        return self._generate_requests()


    def _generate_requests(self):
        requests = []
        unique_listings_ids = Listing.objects.values_list('airbnb_listing_id', flat=True).distinct()
        for listing_id in unique_listings_ids:
            requests.append(self._create_listing_request({"airbnb_listing_id": listing_id}))
        return requests

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
            headers={'X-Airbnb-Api-Key': airbnb_api_key},
            meta={'airbnb_params': listing_data}
        )

    async def parse(self, response: Response, **kwargs) -> None:
        """
        This should be similar to handle_request function in listing spider,
        Need to to find
        """
        pass

