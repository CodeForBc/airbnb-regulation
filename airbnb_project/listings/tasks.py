from celery import shared_task
from twisted.internet import reactor
from scrapy.crawler import CrawlerRunner
from scrapy.utils.log import configure_logging
from listings.harvester_app.harvester.spiders.listings_spider import ListingsSpider
from listings.harvester_app.harvester.harvester_settings import get_harvester_settings
import logging

# Set up logger for the Celery task
logger = logging.getLogger(__name__)

@shared_task(bind=True)
def run_harvest_task(self):
    """
    Celery task to run the Scrapy spider.
    """
    try:
        # Configure Scrapy logging
        configure_logging()

        # Set up the Scrapy crawler with custom settings
        runner = CrawlerRunner(settings=get_harvester_settings())

        # Start the crawling process
        deferred = runner.crawl(ListingsSpider)

        # Add a callback to stop the reactor and log completion
        deferred.addBoth(lambda _: reactor.stop())

        # Start the Twisted reactor (event loop)
        if not reactor.running:
            reactor.run(installSignalHandlers=False)

        logger.info("Scrapy process completed successfully")
    except Exception as e:
        logger.error(f"Error in Scrapy process: {str(e)}")
        raise self.retry(exc=e)
