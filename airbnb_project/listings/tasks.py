from celery import shared_task
from scrapy.crawler import CrawlerProcess
from scrapy.utils.log import configure_logging
from listings.harvester_app.harvester.spiders.listings_spider import ListingsSpider
from listings.harvester_app.harvester.harvester_settings import get_harvester_settings
import logging

logger = logging.getLogger(__name__)

configure_logging()


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


@shared_task(bind=True)
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
    except Exception as e:
        logger.error(f"Error in Scrapy process: {e}")