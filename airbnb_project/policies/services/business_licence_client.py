import json
import requests
from urllib3.exceptions import HTTPError

class BusinessLicenceClient:
    BASE_URL = "https://opendata.vancouver.ca/api/explore/v2.1/catalog/datasets/business-licences/records"

    def __init__(self) -> None:
        self.session = requests.Session()

    def _filter_by_licence_number(self, licence_number: str) -> dict:
        # Omit licence_number validity check since it should be checked during policy evaluation
        return {"where": f'licencenumber="{licence_number}"'}

    def _filter_by_short_term_rental_business(self) -> dict:
        return {"where": 'businesstype="Short-term Rental Operator"'}

    def _licence_status_query(self) -> dict:
        return {"select": "status"}

    def _make_request(self, params: dict) -> dict:
        try:
            response = self.session.get(url=self.BASE_URL, params=params)
            # Raises HTTPError, if one occurred
            response.raise_for_status()
            return response.json()
        except HTTPError as e:
            print(f"Error fetching data: {e}")
            raise e
        except json.JSONDecodeError as e:
            print(f"Error decoding data: {e}")
            raise e

    def _process_licence_status_results(self, response_data: dict) -> list[str]:
        results = response_data["results"]
        # Note: a licence number may have more than 1 status result
        return [result["status"] for result in results]

    def _merge_query_parameters(self, *parameters: dict) -> dict:
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
        """Get a list of status(es) from a licence_number
        Possible statuses: "Issued", "Pending", "Gone Out of Business", "Inactive", "Cancelled"

        For example:
          1. Given licence number "20-247927", return ["Issued"]
          2. Given licence number "20-160574", return ["Pending", "Inactive"]
        """

        params = self._merge_query_parameters(
            self._filter_by_short_term_rental_business(),
            self._filter_by_licence_number(licence_number),
            self._licence_status_query(),
        )
        response_data = self._make_request(params)

        return self._process_licence_status_results(response_data)

if __name__ == "__main__":
    from listings.listing_models import Listing

    example_listing = Listing(
        name="example",
        registration_number="24-225144"
    )
    business_licences = BusinessLicenceClient()
    print(business_licences.get_licence_status(example_listing.registration_number))