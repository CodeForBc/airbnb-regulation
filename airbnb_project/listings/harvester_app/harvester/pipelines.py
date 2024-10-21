# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
import re

from itemadapter import ItemAdapter
from listings.listing_models import Listing
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
    def process_item(self, item, spider):
        try:
            # Check if the listing already exists
            if not Listing.objects.filter(airbnb_listing_id=item.get('airbnb_listing_id', '')).exists():
                # Create and save the new listing if it doesn't exist
                listing = Listing(
                    airbnb_listing_id=item.get('airbnb_listing_id', ''),
                    name=item.get('name', ''),
                    title=item.get('title', ''),
                    baths=item.get('baths', ''),
                    beds=item.get('beds', ''),
                    latitude=item.get('latitude', ''),
                    longitude=item.get('longitude', ''),
                    person_capacity=item.get('person_capacity', ''),
                    registration_number=item.get('registration_number', ''),
                    room_type=item.get('room_type', ''),
                    location=item.get('location', ''),
                    is_bath_shared=item.get('bath_is_shared', ''),
                    baths_text=item.get('baths_text', '')
                )
                # Save the listing to the database
                listing.save()
                spider.logger.info(f"New listing {item.get('listing_id')} saved to the database.")
            else:
                # Log if the listing already exists and is skipped
                spider.logger.info(f"Listing {item.get('listing_id')} already exists, skipping.")
        except IntegrityError as e:
            spider.logger.error(f"Failed to save listing {item.get('name')} to the database: {e}")

        return item
