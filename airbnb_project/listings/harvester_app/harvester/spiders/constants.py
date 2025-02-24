"""
Constants module defining city boundaries for Airbnb URL coordinate generation.
"""
from enum import Enum, auto
from typing import Dict, List, Tuple


class Cities(Enum):
    """Enum representing supported cities."""
    VANCOUVER = auto()


# Defines the bounding box for each city
CITY_COORDINATE_BOUNDARY: Dict[Cities, List[Tuple[float, float]]] = {
    Cities.VANCOUVER: [
        (-123.27242760663955, 49.19990476493376),  # Bottom-left corner (longitude, latitude)
        (-123.02310030521373, 49.29923664124871)   # Top-right corner (longitude, latitude)
    ]
}
