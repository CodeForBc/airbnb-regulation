import unittest
from ..harvester.spiders.constants import Cities, CITY_COORDINATE_BOUNDARY
from ..harvester.spiders.coordinates_builder import AirbnbCoordinatesBuilder

class TestAirbnbCoordinatesBuilder(unittest.TestCase):
    def setUp(self):
        """Set up an instance of AirbnbCoordinatesBuilder for testing."""
        self.builder = AirbnbCoordinatesBuilder()

    def test_build_coordinates_valid_city(self):
        """Test build_coordinates returns expected number of bounding boxes."""
        city = Cities.VANCOUVER
        n = 100  # Subdivisions
        rectangles = self.builder.build_coordinates(city, n)

        self.assertEqual(len(rectangles), n)
        for rect in rectangles:
            self.assertIn("ne_lat", rect)
            self.assertIn("ne_lng", rect)
            self.assertIn("sw_lat", rect)
            self.assertIn("sw_lng", rect)

    def test_build_coordinates_invalid_city(self):
        """Test build_coordinates raises ValueError for an unsupported city."""

        with self.assertRaises(ValueError):
            self.builder.build_coordinates("INVALID_CITY", 100)

    def test_calculate_grid_size(self):
        """Test the _calculate_grid_size method for correct row and column calculations."""
        test_cases = [
            (100, (10, 10)),  # Square grid
            (50, (7, 8)),     # Approximate square
            (3, (1, 3)),      # Small input
            (1, (1, 1)),      # Single cell
        ]

        for n, expected in test_cases:
            with self.subTest(n=n):
                self.assertEqual(self.builder._calculate_grid_size(n), expected)

    def test_generate_bounding_boxes(self):
        """Test _generate_bounding_boxes returns correctly formatted bounding boxes."""
        lon_min, lat_min = -123.2, 49.0  # Southwest corner
        lon_max, lat_max = -123.0, 49.3  # Northeast corner
        num_cols, num_rows = 2, 2  # 2x2 grid

        bounding_boxes = self.builder._generate_bounding_boxes(
            lon_min, lat_min, lon_max, lat_max, num_cols, num_rows
        )

        self.assertEqual(len(bounding_boxes), num_cols * num_rows)
        for rect in bounding_boxes:
            self.assertIn("ne_lat", rect)
            self.assertIn("ne_lng", rect)
            self.assertIn("sw_lat", rect)
            self.assertIn("sw_lng", rect)
            self.assertGreaterEqual(float(rect["ne_lat"]), float(rect["sw_lat"]))
            self.assertGreaterEqual(float(rect["ne_lng"]), float(rect["sw_lng"]))

if __name__ == "__main__":
    unittest.main()
