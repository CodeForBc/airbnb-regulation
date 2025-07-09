import os

"""
Files contains custom settings for the harvester and values related to AirBnB.
"""


def get_harvester_settings():
    # get airbnb public api key for django env
    AIRBNB_PUBLIC_API_KEY = os.environ['AIRBNB_PUBLIC_API_KEY']

    current_directory = os.path.dirname(os.path.abspath(__file__))
    # Construct the absolute path to coordinates.json
    coordinates_file_path = os.path.join(current_directory, 'spiders/listings_django.csv')
    settings_dict = {
        # Values related to AirBnb
        'AIRBNB_PUBLIC_API_KEY': AIRBNB_PUBLIC_API_KEY,
        'AIRBNB_LISTING_API_URL': "https://www.airbnb.ca/api/v3/StaysPdpSections/5bcbb62436650d71839d7e5151d0ee17dd094c931e15f8b0c44ecfbb8d0a3d0b?operationName=StaysPdpSections&locale=en-CA&currency=CAD&variables=%7B%22id%22%3A%22{}%22%2C%22pdpSectionsRequest%22%3A%7B%22adults%22%3A%221%22%2C%22layouts%22%3A%5B%22SINGLE_COLUMN%22%5D%7D%7D&extensions=%7B%22persistedQuery%22%3A%7B%22version%22%3A1%2C%22sha256Hash%22%3A%2237d7cbb631196506c3990783fe194d81432d0fbf7362c668e547bb6475e71b37%22%7D%7D",
        'AIRBNB_SCRIPT_TAG': "data-deferred-state-0",
        'ZOOM_LEVEL': 15.4,

        # Harvester settings
        'BOT_NAME': 'harvester',
        'SPIDER_MODULES': ['listings.harvester_app.harvester.spiders'],
        'NEWSPIDER_MODULE': 'listings.harvester_app.harvester.spiders',
        'CONCURRENT_REQUESTS_PER_DOMAIN': 1,
        'DOWNLOAD_DELAY': 0.02,

        # Custom Settings
        'CSV_STORE_FILE_NAME': coordinates_file_path,
        # Configure item pipelines
        'ITEM_PIPELINES': {
            'listings.harvester_app.harvester.pipelines.AirbnbListingsPipelineDataCleaner': 400,
            'listings.harvester_app.harvester.pipelines.DjangoORMPipeline': 500,

        },

        # Set settings whose default value is deprecated to a future-proof value
        'REQUEST_FINGERPRINTER_IMPLEMENTATION': '2.7',
        'FEED_EXPORT_ENCODING': 'utf-8',
    }

    return settings_dict
