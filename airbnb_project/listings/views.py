from django.http import HttpResponse
from django.views.decorators.http import require_http_methods
from twisted.internet import reactor
from scrapy.crawler import CrawlerRunner
from scrapy.utils.log import configure_logging
from listings.harvester_app.harvester.spiders.listings_spider import ListingsSpider
from listings.harvester_app.harvester.harvester_settings import get_harvester_settings
from threading import Thread
import logging

# Set up logger for this module
logger = logging.getLogger(__name__)

# Global flag to track if the spider is currently running
is_scraping = False


def handle_spider_completion():
    """
    Handle actions to perform when the spider completes crawling.
    """
    global is_scraping
    is_scraping = False
    logger.info(f"Scrapy crawl completed and flag reset. Flag: {is_scraping}")
    logger.info("Scrapy process completed successfully")


def run_spider_in_thread(runner):
    """
    Run the Scrapy spider in a separate thread.
    """
    global is_scraping
    try:
        # Set the flag to indicate that scraping is in progress
        is_scraping = True

        # Start the crawling process
        deferred = runner.crawl(ListingsSpider)

        # Add a callback to reset is_scraping to False and log the completion
        deferred.addBoth(lambda _: handle_spider_completion())

        # Run the reactor (Twisted's event loop)
        if not reactor.running:
            reactor.run(installSignalHandlers=False)

    except Exception as e:
        logger.error(f"Error in Scrapy process: {str(e)}")


@require_http_methods(["GET"])
def harvest_listings(request):
    """
    Django view to initiate the harvesting process.
    """
    global is_scraping
    try:
        if not is_scraping:
            # Configure Scrapy logging
            configure_logging()

            # Set up the Scrapy crawler with custom settings
            runner = CrawlerRunner(settings=get_harvester_settings())

            # Start the spider in a new thread
            thread = Thread(target=run_spider_in_thread, args=(runner,))
            thread.start()
            return HttpResponse("Harvesting process started", status=202)
        else:
            # A harvesting process is already running
            return HttpResponse("A harvesting process is already running", status=409)
    except Exception as e:
        # Log any unexpected errors
        logger.error(f"Failed to start harvesting process: {str(e)}")
        return HttpResponse("Failed to start harvesting process", status=500)
