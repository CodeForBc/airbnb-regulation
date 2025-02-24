"""
Module to generate coordinate-based bounding boxes for Airbnb URL queries.
"""
import json
from abc import ABC, abstractmethod
from typing import List, Dict
from constants import Cities, CITY_COORDINATE_BOUNDARY


class CoordinatesBuilder(ABC):
    """Abstract base class for generating coordinates."""

    @abstractmethod
    def build_coordinates(self, city: Cities, n: int) -> List[Dict[str, str]]:
        """
        Generates a list of bounding boxes for a given city.

        :param city: The city for which coordinates should be generated.
        :param n: The number of subdivisions (bounding boxes) required.
        :return: A list of bounding boxes, each represented as a dictionary.
        """
        pass


class AirbnbCoordinatesBuilder(CoordinatesBuilder):
    """Concrete implementation of CoordinatesBuilder to generate Airbnb coordinate grids."""

    def build_coordinates(self, city: Cities, n: int) -> List[Dict[str, str]]:
        """
        Generates a list of bounding boxes for Airbnb listings in the given city.

        :param city: The city for which coordinates should be generated.
        :param n: The number of subdivisions (bounding boxes) required.
        :return: A list of bounding boxes.
        """
        if city not in CITY_COORDINATE_BOUNDARY:
            raise ValueError(f"City {city.name} is not supported.")

        bbox = CITY_COORDINATE_BOUNDARY[city]
        lon_min, lat_min = bbox[0]  # Bottom-left corner
        lon_max, lat_max = bbox[1]  # Top-right corner

        num_cols, num_rows = self._calculate_grid_size(n)

        return self._generate_bounding_boxes(lon_min, lat_min, lon_max, lat_max, num_cols, num_rows)

    def _calculate_grid_size(self, n: int) -> (int, int):
        """
        Determines the number of rows and columns for the grid subdivision.

        :param n: The total number of bounding boxes.
        :return: Tuple of (num_cols, num_rows).
        """
        num_cols = int(n ** 0.5)  # Approximate square grid
        num_rows = (n + num_cols - 1) // num_cols  # Ensures we cover n regions
        return num_cols, num_rows

    def _generate_bounding_boxes(
            self, lon_min: float, lat_min: float, lon_max: float, lat_max: float, num_cols: int, num_rows: int
    ) -> List[Dict[str, str]]:
        """
        Generates a list of bounding boxes covering the given area.

        :param lon_min: Minimum longitude (west).
        :param lat_min: Minimum latitude (south).
        :param lon_max: Maximum longitude (east).
        :param lat_max: Maximum latitude (north).
        :param num_cols: Number of columns in the grid.
        :param num_rows: Number of rows in the grid.
        :return: A list of bounding boxes in dictionary format.
        """
        bounding_boxes = []
        rect_width = (lon_max - lon_min) / num_cols
        rect_height = (lat_max - lat_min) / num_rows

        for row in range(num_rows):
            for col in range(num_cols):
                bottom_left_lon = lon_min + col * rect_width
                bottom_left_lat = lat_min + row * rect_height
                top_right_lon = min(bottom_left_lon + rect_width, lon_max)
                top_right_lat = min(bottom_left_lat + rect_height, lat_max)

                bounding_boxes.append({
                    "ne_lat": str(top_right_lat),
                    "ne_lng": str(top_right_lon),
                    "sw_lat": str(bottom_left_lat),
                    "sw_lng": str(bottom_left_lon)
                })

        return bounding_boxes
