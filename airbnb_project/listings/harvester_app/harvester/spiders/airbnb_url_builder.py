from datetime import datetime, timedelta

"""
Values for the months that are used in the url builder
"""


class AirBnbURLBuilder:
    """
    A class for building AirBnb URLs for web scraping purposes.

    This class provides methods to generate various types of AirBnb search URLs
    for Vancouver, Canada, including flexible date searches and specific date ranges.
    """
    AirBnbMonths = [
        "january",
        "february",
        "march",
        "april",
        "may",
        "june",
        "july",
        "august",
        "september",
        "october",
        "november",
        "december",
    ]
    SCHEME = "https"
    BASE_URL = "www.airbnb.ca"
    HOMES_PATH = "s/Vancouver--Canada/homes"
    DEFAULT_PARAMS = {
        "ne_lat": {},
        "ne_lng": {},
        "sw_lat": {},
        "sw_lng": {},
        "zoom_level": {},
        "zoom": {},
        "search_by_map": "true",
        "tab_id": "home_tab",
        "refinement_paths[]": "/homes",
        "query": "Vancouver, BC",
        "place_id": "ChIJs0-pQ_FzhlQRi_OBm-qWkbs"
    }

    @staticmethod
    def get_params_string(params):
        """
        Convert a dictionary of parameters into a URL query string.

        Args:
            params (dict): A dictionary of parameter key-value pairs.

        Returns:
            str: A URL-encoded query string.
        """
        output = ""
        for key, value in params.items():
            if isinstance(value, tuple):
                for item in value:
                    output += f"{key}={item}&"
            else:
                output += f"{key}={value}&"
        return output[:-1]

    def get_urls(self, *months):
        """
        Generate a list of URLs for different search types.

        Args:
            *months: Variable length argument list of month names.

        Returns:
            list: A list of URLs for flexible month, week, weekend, multi-month, and specific date searches.
        """
        if not len(months):
            months = self._get_current_months()
        check_in, check_out = self.get_date()
        check_in_month, check_out_month = self.get_date(time_delta=90)
        return [self.get_flexible_month(*months), self.get_flexible_week(*months), self.get_flexible_weekend(*months),
                self.get_months(check_in_month, check_out_month), self.get_dates(check_in, check_out)]

    def _get_full_url(self, param):
        """
        Construct a full URL using the given parameters.

        Args:
            param (dict): A dictionary of URL parameters.

        Returns:
            str: A complete AirBnb search URL.
        """
        return f"{AirBnbURLBuilder.SCHEME}://{AirBnbURLBuilder.BASE_URL}/{AirBnbURLBuilder.HOMES_PATH}?{AirBnbURLBuilder.get_params_string(param)}"

    def get_flexible_week(self, *month):
        """
        Generate a URL for a flexible one-week stay.

        Args:
            *month: Variable length argument list of month names. If none provided, uses the current month.

        Returns:
            str: A URL for a flexible one-week stay search.
        """
        if not len(month):
            month = self._get_current_months(number_of_months=1)
        local_param = AirBnbURLBuilder.DEFAULT_PARAMS.copy()
        local_param['flexible_trip_lengths[]'] = "one_week"
        local_param['flexible_trip_dates[]'] = month
        return self._get_full_url(local_param)

    def get_flexible_weekend(self, *month):
        """
        Generate a URL for a flexible weekend stay.

        Args:
            *month: Variable length argument list of month names. If none provided, uses the current month.

        Returns:
            str: A URL for a flexible weekend stay search.
        """
        if not len(month):
            month = self._get_current_months(number_of_months=1)
        local_param = AirBnbURLBuilder.DEFAULT_PARAMS.copy()
        local_param['flexible_trip_lengths[]'] = "weekend_trip"
        local_param['flexible_trip_dates[]'] = month
        return self._get_full_url(local_param)

    def get_flexible_month(self, *month):
        """
        Generate a URL for a flexible one-month stay.

        Args:
            *month: Variable length argument list of month names. If none provided, uses the current month.

        Returns:
            str: A URL for a flexible one-month stay search.
        """
        if not len(month):
            month = self._get_current_months(number_of_months=1)
        local_param = AirBnbURLBuilder.DEFAULT_PARAMS.copy()
        local_param['flexible_trip_lengths[]'] = "one_month"
        local_param['flexible_trip_dates[]'] = month
        return self._get_full_url(local_param)

    def get_dates(self, check_in, check_out):
        """
        Generate a URL for a specific date range search.

        Args:
            check_in (str): Check-in date in 'YYYY-MM-DD' format.
            check_out (str): Check-out date in 'YYYY-MM-DD' format.

        Returns:
            str: A URL for a specific date range search.
        """
        local_param = AirBnbURLBuilder.DEFAULT_PARAMS.copy()
        local_param['checkin'] = check_in
        local_param['checkout'] = check_out
        local_param['flexible_date_search_filter_type'] = "1"
        return self._get_full_url(local_param)

    def get_months(self, check_in, check_out, length=3):
        """
        Generate a URL for a multi-month stay search.

        Args:
            check_in (str): Start date of the stay in 'YYYY-MM-DD' format.
            check_out (str): End date of the stay in 'YYYY-MM-DD' format.
            length (int): Number of months for the stay. Default is 3.

        Returns:
            str: A URL for a multi-month stay search.
        """
        local_param = AirBnbURLBuilder.DEFAULT_PARAMS.copy()
        local_param['monthly_start_date'] = check_in
        local_param['monthly_end_date'] = check_out
        local_param['monthly_length'] = length
        local_param['flexible_date_search_filter_type'] = "6"
        return self._get_full_url(local_param)

    def _get_current_months(self, number_of_months=3):
        """
        Get the names of the current and upcoming months, wrapping around if necessary.

        Args:
            number_of_months (int): Number of months to retrieve, including the current month.
            Should be less than or equal to 12.

        Returns:
            tuple: The names of the current and upcoming months in lowercase.
        """
        # Ensure number_of_months is at most 12
        number_of_months = min(number_of_months, 12)
        current_month = datetime.now().month - 1
        end_month = (current_month + number_of_months) % len(AirBnbURLBuilder.AirBnbMonths)
        if end_month > current_month:
            return tuple(AirBnbURLBuilder.AirBnbMonths[current_month:end_month])
        else:
            # Wrap around
            return tuple(AirBnbURLBuilder.AirBnbMonths[current_month:] + AirBnbURLBuilder.AirBnbMonths[:end_month])

    def get_date(self, start_date=None, time_delta=5):
        """
        Generate check-in and check-out dates.

        Args:
            start_date (datetime, optional): The start date. If None, uses the current date.
            time_delta (int, optional): Number of days between check-in and check-out. Default is 5.

        Returns:
            tuple: A tuple containing check-in and check-out dates as strings in 'YYYY-MM-DD' format.
        """
        # Get the current date
        check_in = datetime.now() if start_date is None else start_date
        check_in_string = check_in.strftime("%Y-%m-%d")
        # Add the days to the current date
        check_out = check_in + timedelta(days=time_delta)
        # Format the new date
        check_out_string = check_out.strftime("%Y-%m-%d")

        return check_in_string, check_out_string
