# Scrapy settings for airbnb_listings project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     https://docs.scrapy.org/en/latest/topics/settings.html
#     https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
#     https://docs.scrapy.org/en/latest/topics/spider-middleware.html
BOT_NAME = "harvester"

SPIDER_MODULES = ["harvester.spiders"]
NEWSPIDER_MODULE = "harvester.spiders"


CONCURRENT_REQUESTS_PER_DOMAIN = 1

# Delay between each request in seconds
DOWNLOAD_DELAY = 0.02

# Sets the name of csv file in which the listings are saved
CSV_STORE_FILE_NAME = 'listings.csv'

# Sets the feed so that listings are saved automatically to a csv when the crawler is run
FEEDS = {
    CSV_STORE_FILE_NAME: {'format': "csv", "overwrite": False}
}

# Obey robots.txt rules
ROBOTSTXT_OBEY = False

# Enable or disable downloader middlewares
# See https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
DOWNLOADER_MIDDLEWARES = {}

# Enable or disable extensions
# See https://docs.scrapy.org/en/latest/topics/extensions.html
# EXTENSIONS = {
#    "scrapy.extensions.telnet.TelnetConsole": None,
# }

# Configure item pipelines
# See https://docs.scrapy.org/en/latest/topics/item-pipeline.html
ITEM_PIPELINES = {
    # "airbnb_listings.pipelines.AirBnbListingsDuplicatePipeLine": 300,
    "harvester.pipelines.AirbnbListingsPipelineDataCleaner": 400,
    # "harvester.pipelines.DatabaseStoragePipeline": 500,
}


# Set settings whose default value is deprecated to a future-proof value
REQUEST_FINGERPRINTER_IMPLEMENTATION = "2.7"
FEED_EXPORT_ENCODING = "utf-8"
