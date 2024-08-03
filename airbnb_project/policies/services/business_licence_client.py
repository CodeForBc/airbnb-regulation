import json
import requests
import logging
from urllib3.exceptions import HTTPError

class BusinessLicenceClient:
    BASE_URL = "https://opendata.vancouver.ca/api/explore/v2.1/catalog/datasets/business-licences/records"

    def __init__(self) -> None:
        """
        Initialize the BusinessLicenceClient with a session.
        """
        self.session = requests.Session()

    def _filter_by_licence_number(self, licence_number: str) -> dict:
        """
        Generate query parameters to filter results by licence number.
        
        Args:
            licence_number (str): The licence number to filter by.
        
        Returns:
            dict: Query parameters for filtering by licence number.
        """
        return {"where": f'licencenumber="{licence_number}"'}

    def _filter_by_short_term_rental_business(self) -> dict:
        """
        Generate query parameters to filter results by short-term rental business type.
        
        Returns:
            dict: Query parameters for filtering by short-term rental business type.
        """
        return {"where": 'businesstype="Short-term Rental Operator"'}

    def _get_latest_licence_status(self) -> dict:
        """
        Generate query parameters to select the licence status by the latest licence revision.
        
        Returns:
            dict: Query parameters for selecting latest licence status.
        """
        return {
          "select": "status",
          "order_by": "licencerevisionnumber desc",
          "limit": "1"
        }

    def _make_request(self, params: dict) -> dict:
        """
        Make an API request to the specified URL with given parameters.
        
        Args:
            params (dict): Query parameters for the request.
        
        Returns:
            dict: The JSON response from the API.
        
        Raises:
            HTTPError: If an HTTP error occurs.
            json.JSONDecodeError: If there is an error decoding the JSON response.
        """
        try:
            response = self.session.get(url=self.BASE_URL, params=params)
            # Raises HTTPError, if one occurred
            response.raise_for_status()
            return response.json()
        except HTTPError as e:
            logging.error(f"Error fetching data: {e}")
            raise e
        except json.JSONDecodeError as e:
            logging.error(f"Error decoding data: {e}")
            raise e

    def _process_licence_status_results(self, response_data: dict) -> str:
        """
        Process the API response data to extract the licence status.
        
        Args:
            response_data (dict): The JSON response data from the API.
        
        Returns:
            str: Licence status.
        """
        try:
          results = response_data.get("results", [])
          if not results:
            logging.warning("No results found in response data.")
            return "No results found"
        
          # Get status in results
          status = results[0].get("status")
          
          if not status:
            logging.warning("Status not found in the first result.")
            return "Status not found"
          
          return status
        
        except (KeyError, IndexError, TypeError) as e:
          logging.error(f"Error processing response data: {e}")
          return "Error processing data"

    def _merge_query_parameters(self, *parameters: dict) -> dict:
        """
        Merge multiple query parameters into a single dictionary.
        
        Args:
            *parameters (dict): Query parameters to merge.
        
        Returns:
            dict: Merged query parameters.
        """
        merged_query_parameter = {}
        for parameter in parameters:
            for key, value in parameter.items():
                if key in merged_query_parameter:
                    merged_query_parameter[key] = " and ".join(
                        [merged_query_parameter[key], value]
                    )
                else:
                    merged_query_parameter[key] = value
        return merged_query_parameter

    def get_licence_status(self, licence_number: str) -> list[str]:
        """
        Get a status from a licence number.
        
        Possible statuses: "Issued", "Pending", "Gone Out of Business", "Inactive", "Cancelled".
        
        Args:
            licence_number (str): The licence number to check status for.
        
        Returns:
            list[str]: A list of statuses for the given licence number.
        
        Examples:
            1. Given licence number "24-159412", return "Issued".
            2. Given licence number "24-243792", return "Cancelled".
        """

        params = self._merge_query_parameters(
            self._filter_by_short_term_rental_business(),
            self._filter_by_licence_number(licence_number),
            self._get_latest_licence_status(),
        )
        response_data = self._make_request(params)

        return self._process_licence_status_results(response_data)