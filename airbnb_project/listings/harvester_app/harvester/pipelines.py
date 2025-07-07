# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html
import json
# useful for handling different item types with a single interface
import re

from django.core.exceptions import ValidationError
from itemadapter import ItemAdapter
from listings.listing_models import Listing, ListingHost
from django.db.utils import IntegrityError


class AirbnbListingsPipelineDataCleaner:
    """
    A pipeline for cleaning Airbnb listing data.

    This class processes items scraped by the spider, performing data cleaning
    and transformation operations on specific fields.

    Attributes:
    - fields_to_lower_case (list): A list of field names to convert to lowercase.
    """

    fields_to_lower_case = ["title", "name"]

    def process_item(self, item, spider):
        """
        Process an item from the spider.

        This method performs several data cleaning operations:
        1. Extracts the number of beds from the 'beds' field.
        2. Extracts the number of bathrooms from the 'baths_text' field.
        3. Determines if the bathroom is shared based on the 'baths_text' field.

        Args:
        - item (dict): The item to process, containing scraped Airbnb listing data.
        - spider: The spider that crawled the item (unused in this method).

        Returns:
        - dict: The processed item with cleaned and transformed data.
        """
        adapter = ItemAdapter(item)

        self._extract_beds(adapter)
        self._extract_bathrooms(adapter)

        return item

    def _extract_beds(self, adapter):
        """
        Extract the number of beds from the 'beds' field.

        Args:
        - adapter (ItemAdapter): The item adapter containing the listing data.
        """
        un_formatted_beds = adapter.get('beds')
        beds = None

        pattern = r'^\d+'
        try:
            match = re.search(pattern, un_formatted_beds)
            if match:
                beds = match.group()
            else:
                beds = None
        except Exception as e:
            print(f"Error extracting beds: {e}")

        adapter['beds'] = beds

    def _extract_bathrooms(self, adapter):
        """
        Extract bathroom information from the 'baths_text' field.

        This method extracts the number of bathrooms and determines if the
        bathroom is shared based on the 'baths_text' field.

        Args:
        - adapter (ItemAdapter): The item adapter containing the listing data.
        """
        un_formatted_bathrooms = adapter.get('baths_text')
        bathroom = None

        pattern = r'^\d+\.?\d*'
        pattern_two = r'(?i)\bhalf-bath\b'
        try:
            if "shared" in un_formatted_bathrooms:
                adapter['bath_is_shared'] = True
            else:
                adapter['bath_is_shared'] = False

            match = re.search(pattern, un_formatted_bathrooms)
            if match:
                bathroom = match.group()
            else:
                match = re.search(pattern_two, un_formatted_bathrooms)
                if match:
                    bathroom = 0.5
                elif un_formatted_bathrooms.strip() == "":
                    bathroom = None
        except Exception as e:
            print(f"Error extracting bathrooms: {e}")

        adapter['baths'] = bathroom



class DjangoORMPipeline:
    """
    A Django ORM pipeline for processing and storing Airbnb listing and host data.

    This pipeline handles the creation of new Listing and ListingHost objects in the database.
    It ensures that no duplicate listings are created based on the airbnb_listing_id,
    and that host data is correctly associated with each listing.
    All fields are required and must be present in the input item. The pipeline includes
    error handling for database integrity issues and logging capabilities for monitoring the data flow.
    """

    def process_item(self, item, spider):
        """
        Process a scraped item and store it in the database if valid and unique.

        Args:
            item (dict): A dictionary containing scraped Airbnb listing data with these required keys:
                - airbnb_listing_id (str): Unique identifier for the Airbnb listing
                - name (str): Name of the listing
                - title (str): Title of the listing
                - baths (str): Number of bathrooms
                - beds (str): Number of beds
                - latitude (str): Latitude coordinate
                - longitude (str): Longitude coordinate
                - person_capacity (str): Maximum number of guests
                - registration_number (str): Official registration number
                - room_type (str): Type of room/accommodation
                - location (str): Location description
                - bath_is_shared (bool): Whether bathroom is shared
                - baths_text (str): Textual description of bathroom facilities
                - host information (dictionary with host details)
            spider: The spider instance that is running the crawl

        Returns:
            dict: The original item dictionary, unmodified

        Note:
            - All fields are required - missing or empty airbnb_listing_id will cause the item to be logged and skipped
            - If a listing with the same airbnb_listing_id exists, it will be skipped
        """

        airbnb_listing_id = item.get('airbnb_listing_id', '')

        # Early return if no valid airbnb_listing_id
        if not airbnb_listing_id:
            spider.logger.error(f"Missing required airbnb_listing_id, skipping item, item Details\n{json.dumps(item)}")
            return item

        # Extract host information from the item
        host_info = {
            'user_id': item.get('user_id'),
            'name': item.get('host_name'),
            'title_text': item.get('title_text'),
            'profile_picture_url': item.get('profile_picture_url'),
            'thumbnail_url': item.get('thumbnail_url'),
            'is_verified': item.get('is_verified', False),
            'is_superhost': item.get('is_superhost', False),
            'rating_count': item.get('rating_count', 0),
            'rating_average': item.get('rating_average', 0),
            'time_as_host_years': item.get('time_as_host_years', 0),
            'time_as_host_months': item.get('time_as_host_months', 0),
        }

        # Create or update the ListingHost if host information is available
        host = None
        if host_info['user_id']:
            host, created = ListingHost.objects.get_or_create(
                user_id=host_info['user_id'],
                defaults=host_info
            )
            if created:
                spider.logger.info(f"New host {host_info['user_id']} created.")
            else:
                spider.logger.info(f"Host {host_info['user_id']} already exists.")

        try:
            # Create or update the Listing object
            listing = Listing(
                airbnb_listing_id=item.get('airbnb_listing_id'),
                name=item.get('name'),
                title=item.get('title'),
                baths=item.get('baths'),
                beds=item.get('beds'),
                latitude=item.get('latitude'),
                longitude=item.get('longitude'),
                person_capacity=item.get('person_capacity'),
                registration_number=item.get('registration_number'),
                room_type=item.get('room_type'),
                location=item.get('location'),
                is_bath_shared=item.get('bath_is_shared'),
                baths_text=item.get('baths_text'),
                host=host  # Link the host to the listing
            )

            # Save the listing to the database
            listing.save()
            spider.logger.info(f"New listing {item.get('airbnb_listing_id')} saved to the database.")

        except IntegrityError as e:
            spider.logger.error(f"Failed to save listing {item.get('airbnb_listing_id')} to the database: {e}")
        except Exception as e:
            spider.logger.error(f"Failed to save listing {item.get('name')} to the database: {e}")

        return item
