from celery import shared_task
from celery.exceptions import SoftTimeLimitExceeded, TimeLimitExceeded
from scrapy.crawler import CrawlerProcess
from scrapy.utils.log import configure_logging
from listings.harvester_app.harvester.spiders.listings_spider import (
    ListingsSpider, base64_encode_string, combine_and_url_encode
)
from listings.harvester_app.harvester.harvester_settings import get_harvester_settings
from listings.harvester_app.harvester.items import ExpandedAirBnBListingItem
from listings.harvester_app.harvester.pipelines import AirbnbListingsPipelineDataCleaner, DjangoORMPipeline
from django.conf import settings
import requests
import os
import json
import logging
from billiard.context import Process

logger = logging.getLogger(__name__)

configure_logging(settings={
    'LOG_FORMAT': '%(asctime)s [%(name)s] %(levelname)s %(filename)s:%(funcName)s:%(lineno)d: %(message)s'
})


def run_spider():
    """
    Run the Scrapy spider for harvesting listings.

    This function initializes a Scrapy CrawlerProcess with the required settings,
    schedules the `ListingsSpider` to run, and starts the crawling process.
    The function runs in non-blocking mode with `stop_after_crawl=False` to keep
    the process active after the spider completes.

    Returns:
        None
    """
    runner = CrawlerProcess(settings=get_harvester_settings())
    runner.crawl(ListingsSpider)
    runner.start(stop_after_crawl=False)
    
    def _run():
        try:
            runner = CrawlerProcess(settings=get_harvester_settings())
            runner.crawl(ListingsSpider)
            runner.start()  # This blocks until finished
        except Exception as e:
            logger.error(f"Spider subprocess failed: {e}")

    p = Process(target=_run)
    p.start()
    p.join()

@shared_task(bind=True, retry_kwargs={'max_retries': 1}, ignore_result=True, time_limit=3600, soft_time_limit=3400)
def run_harvest_task(self):
    """
    Celery task to trigger the Scrapy spider for harvesting listings.

    This task runs the `run_spider` function to start the spider process.
    It handles any exceptions during the spider execution and logs success
    or error messages.

    Args:
        self: Reference to the current Celery task instance.

    Returns:
        None
    """
    try:
        # Run the spider and wait for it to complete
        run_spider()
        logger.info("Scrapy process completed successfully")
    except SoftTimeLimitExceeded:
        print("Soft time limit exceeded. Cleaning up...")
    except TimeLimitExceeded:
        print("Time limit exceeded. Cleaning up...")
    except Exception as e:
        logger.error(f"Error in Scrapy process: {e}")


@shared_task(ignore_result=False)
def run_refresh_single_listing(listing_id):
    """
    Fetch, parse, and store a single Airbnb listing by ID.
    Reuses Spider parsing logic and Item Pipelines.
    """
    try:
        # Use harvester settings as the single source of truth for API configuration
        h_settings = get_harvester_settings()
        api_url_template = h_settings.get('AIRBNB_LISTING_API_URL')
        api_key = h_settings.get('AIRBNB_PUBLIC_API_KEY')

        if not api_url_template or not api_key:
            logger.error("Missing AIRBNB_LISTING_API_URL or AIRBNB_PUBLIC_API_KEY in harvester settings.")
            return
        
        encoded_id = base64_encode_string(combine_and_url_encode("StayListing", listing_id))
        url = api_url_template.format(encoded_id)
        logger.info(f"Fetching listing {listing_id} from Airbnb API at {url}")

        # 2. Fetch the data
        response = requests.get(url, headers={'X-Airbnb-Api-Key': api_key})
        if response.status_code != 200:
            logger.error(f"Airbnb API returned {response.status_code} for listing {listing_id}")
            return

        data = response.json()
        
        # 3. Initialize Item with basic ID
        # Note: Since we skip search, we rely on PDP parsing for names/locations
        item = ExpandedAirBnBListingItem(airbnb_listing_id=listing_id)

        # 4. Use existing Spider static methods to populate the item
        ListingsSpider._parse_capacity_and_location(data, item)
        ListingsSpider._parse_listings_number(data, item)
        ListingsSpider._parse_host_id(data, item)
        
        # Extract basic info that might be missing because we skipped the search results phase
        metadata = ListingsSpider._get_metadata_from_json(data)
        sharing_config = metadata.get('sharingConfig', {})
        
        # Fallbacks for fields usually provided by search result params
        item['name'] = item.get('name') or sharing_config.get('title')
        item['title'] = item.get('title') or sharing_config.get('title')
        item['location'] = item.get('location') or sharing_config.get('location')
        
        # 5. Run through Pipelines
        # Mock a spider object for the pipelines (they expect a spider for logging)
        mock_spider = type('MockSpider', (object,), {'logger': logger})()
        
        cleaner = AirbnbListingsPipelineDataCleaner()
        orm_pipeline = DjangoORMPipeline()

        # Process cleaning
        item = cleaner.process_item(item, mock_spider)
        # Save to DB
        orm_pipeline.process_item(item, mock_spider)


        logger.info(f"Successfully refreshed listing {listing_id}: {json.dumps(item, default=str)}")

    except Exception as e:
        logger.error(f"Failed to refresh listing {listing_id}: {str(e)}", exc_info=True)
