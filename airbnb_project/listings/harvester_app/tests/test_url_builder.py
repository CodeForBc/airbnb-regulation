import unittest
from datetime import datetime
from airbnb_project.listings.harvester_app.harvester.spiders.airbnb_url_builder import AirBnbURLBuilder


class TestAirBnbURLBuilder(unittest.TestCase):
    def setUp(self):
        self.builder = AirBnbURLBuilder()

    def test_get_params_string(self):
        params = {
            "ne_lat": 49.2827,
            "ne_lng": -123.1207,
            "sw_lat": 49.2060,
            "sw_lng": -123.1789,
            "zoom_level": 12,
            "zoom": 11,
            "search_by_map": "true",
            "tab_id": "home_tab",
            "refinement_paths[]": "/homes",
            "query": "Vancouver, BC",
            "place_id": "ChIJs0-pQ_FzhlQRi_OBm-qWkbs"
        }
        expected_output = "ne_lat=49.2827&ne_lng=-123.1207&sw_lat=49.206&sw_lng=-123.1789&zoom_level=12&zoom=11&search_by_map=true&tab_id=home_tab&refinement_paths[]=/homes&query=Vancouver, BC&place_id=ChIJs0-pQ_FzhlQRi_OBm-qWkbs"
        self.assertEqual(AirBnbURLBuilder.get_params_string(params), expected_output)

    def test_get_flexible_week(self):
        expected_url = "https://www.airbnb.ca/s/Vancouver--Canada/homes?ne_lat={}&ne_lng={}&sw_lat={}&sw_lng={}&zoom_level={}&zoom={}&search_by_map=true&tab_id=home_tab&refinement_paths[]=/homes&query=Vancouver, BC&place_id=ChIJs0-pQ_FzhlQRi_OBm-qWkbs&flexible_trip_lengths[]=one_week&flexible_trip_dates[]=august"
        self.assertEqual(self.builder.get_flexible_week("august"), expected_url)

    def test_get_flexible_weekend(self):
        expected_url = "https://www.airbnb.ca/s/Vancouver--Canada/homes?ne_lat={}&ne_lng={}&sw_lat={}&sw_lng={}&zoom_level={}&zoom={}&search_by_map=true&tab_id=home_tab&refinement_paths[]=/homes&query=Vancouver, BC&place_id=ChIJs0-pQ_FzhlQRi_OBm-qWkbs&flexible_trip_lengths[]=weekend_trip&flexible_trip_dates[]=august"
        self.assertEqual(self.builder.get_flexible_weekend("august"), expected_url)

    def test_get_flexible_month(self):
        expected_url = "https://www.airbnb.ca/s/Vancouver--Canada/homes?ne_lat={}&ne_lng={}&sw_lat={}&sw_lng={}&zoom_level={}&zoom={}&search_by_map=true&tab_id=home_tab&refinement_paths[]=/homes&query=Vancouver, BC&place_id=ChIJs0-pQ_FzhlQRi_OBm-qWkbs&flexible_trip_lengths[]=one_month&flexible_trip_dates[]=august"
        self.assertEqual(self.builder.get_flexible_month("august"), expected_url)

    def test_get_dates(self):
        check_in = "2023-08-01"
        check_out = "2023-08-06"
        expected_url = "https://www.airbnb.ca/s/Vancouver--Canada/homes?ne_lat={}&ne_lng={}&sw_lat={}&sw_lng={}&zoom_level={}&zoom={}&search_by_map=true&tab_id=home_tab&refinement_paths[]=/homes&query=Vancouver, BC&place_id=ChIJs0-pQ_FzhlQRi_OBm-qWkbs&checkin=2023-08-01&checkout=2023-08-06&flexible_date_search_filter_type=1"
        self.assertEqual(self.builder.get_dates(check_in, check_out), expected_url)

    def test_get_months(self):
        check_in = "2023-08-01"
        check_out = "2023-10-31"
        expected_url = "https://www.airbnb.ca/s/Vancouver--Canada/homes?ne_lat={}&ne_lng={}&sw_lat={}&sw_lng={}&zoom_level={}&zoom={}&search_by_map=true&tab_id=home_tab&refinement_paths[]=/homes&query=Vancouver, BC&place_id=ChIJs0-pQ_FzhlQRi_OBm-qWkbs&monthly_start_date=2023-08-01&monthly_end_date=2023-10-31&monthly_length=3&flexible_date_search_filter_type=6"
        self.assertEqual(self.builder.get_months(check_in, check_out), expected_url)

    def test_get_date(self):
        start_date = datetime(2023, 8, 1)
        check_in, check_out = self.builder.get_date(start_date)
        self.assertEqual(check_in, "2023-08-01")
        self.assertEqual(check_out, "2023-08-06")

    def test_get_current_months(self):
        current_months = ("august", "september", "october")
        get_months = self.builder._get_current_months()
        self.assertEqual(current_months, get_months)


if __name__ == '__main__':
    unittest.main()
