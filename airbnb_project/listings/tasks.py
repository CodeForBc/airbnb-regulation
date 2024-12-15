from celery import shared_task
from twisted.internet import reactor, defer
from scrapy.crawler import CrawlerRunner, CrawlerProcess
from scrapy.utils.log import configure_logging
from listings.harvester_app.harvester.spiders.listings_spider import ListingsSpider
from listings.harvester_app.harvester.harvester_settings import get_harvester_settings
import logging
from crochet import setup, wait_for

logger = logging.getLogger(__name__)

configure_logging()


def run_spider():
    """
    Run the spider and return a deferred that will fire when the spider completes.
    """
    runner = CrawlerProcess(settings=get_harvester_settings())
    runner.crawl(ListingsSpider)
    runner.start(stop_after_crawl=False)


@shared_task(bind=True)
def run_harvest_task(self):
    """
    Celery task to run the Scrapy spider.
    """
    try:
        # Run the spider and wait for it to complete
        run_spider()
        logger.info("Scrapy process completed successfully")
    except Exception as e:
        logger.error(f"Error in Scrapy process: {e}")
