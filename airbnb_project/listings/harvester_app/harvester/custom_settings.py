import os

"""
Files contains custom settings for the harvester and values related to AirBnB.
"""


def get_scrapy_settings():
    current_directory = os.path.dirname(os.path.abspath(__file__))
    # Construct the absolute path to coordinates.json
    coordinates_file_path = os.path.join(current_directory, 'spiders/listings.csv')
    settings_dict = {
        # Values related to AirBnb
        'AIRBNB_PUBLIC_API_KEY': "",
        'AIRBNB_LISTING_API_URL': "https://www.airbnb.ca/api/v3/StaysPdpSections/08e3ad2e3d75c9bede923485718ff2e7f6efe2ca1febb5192d78c51e17e8b4ca?operationName=StaysPdpSections&locale=en-CA&currency=CAD&variables=%7B%22id%22%3A%22{}%22%2C%22pdpSectionsRequest%22%3A%7B%22adults%22%3A%221%22%2C%22layouts%22%3A%5B%22SINGLE_COLUMN%22%5D%7D%7D&extensions=%7B%22persistedQuery%22%3A%7B%22version%22%3A1%2C%22sha256Hash%22%3A%2237d7cbb631196506c3990783fe194d81432d0fbf7362c668e547bb6475e71b37%22%7D%7D",
        'AIRBNB_SCRIPT_TAG': "data-deferred-state-0",
        'ZOOM_LEVEL': 15.4,

        # Harvester settings
        'BOT_NAME': 'harvester',
        'SPIDER_MODULES': ['airbnb_project.listings.harvester_app.harvester.spiders'],
        'NEWSPIDER_MODULE': 'airbnb_project.listings.harvester_app.harvester.spiders',

        'CONCURRENT_REQUESTS_PER_DOMAIN': 1,
        'DOWNLOAD_DELAY': 0.02,

        # Custom Settings
        'CSV_STORE_FILE_NAME': coordinates_file_path,
        'FEEDS': {
            coordinates_file_path: {'format': 'csv', 'overwrite': False},
        },
        # Configure item pipelines
        'ITEM_PIPELINES': {
            'airbnb_project.listings.harvester_app.harvester.pipelines.AirbnbListingsPipelineDataCleaner': 400,
        },

        # Set settings whose default value is deprecated to a future-proof value
        'REQUEST_FINGERPRINTER_IMPLEMENTATION': '2.7',
        'FEED_EXPORT_ENCODING': 'utf-8',
    }

    return settings_dict
