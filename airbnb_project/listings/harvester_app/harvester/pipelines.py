# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
import re
import sqlite3

from itemadapter import ItemAdapter


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


class DatabaseStoragePipeline:

    def __init__(self):
        self.con = sqlite3.connect('airbnb.db')
        self.cur = self.con.cursor()
        self.create_table()

    def create_table(self):
        self.cur.execute("""
        Create TABLE IF NOT EXISTS listings(
        airbnb_listing_id INTEGER PRIMARY KEY,
        baths INTEGER,
        beds INTEGER,
        latitude FLOAT,
        longitude FLOAT,
        name TEXT,
        person_capacity INTEGER,
        registration_number TEXT,
        room_type TEXT,
        title TEXT,
        is_bath_shared INTEGER,
        baths_text TEXT
        )
        """)

    def process_item(self, item, spider):
        bath_is_shared = 1 if item.get('bath_is_shared') else 0
        self.cur.execute(
            """INSERT OR IGNORE INTO listings VALUES (?,?,?,?,?,?,?,?,?,?,?,?)"""
            , (
                item['airbnb_listing_id'],
                item['baths'],
                item['beds'],
                item['latitude'],
                item['longitude'],
                item['name'],
                item['person_capacity'],
                item['registration_number'],
                item['room_type'],
                item['title'],
                bath_is_shared,
                item['baths_text'],
            ))
        self.con.commit()
        return item
