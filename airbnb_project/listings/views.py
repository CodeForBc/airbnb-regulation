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


def run_spider_in_thread(runner):
    """
    Run the Scrapy spider in a separate thread.

    This function is designed to be run in a separate thread to avoid
    blocking the main Django process. It handles the Scrapy crawling
    process and manages the reactor.

    Args:
        runner (CrawlerRunner): The configured Scrapy crawler runner.

    Returns:
        None
    """
    try:
        # Start the crawling process
        deferred = runner.crawl(ListingsSpider)
        # Add a callback to stop the reactor when crawling is finished
        deferred.addBoth(lambda _: reactor.stop())
        # Run the reactor (Twisted's event loop)
        reactor.run(installSignalHandlers=False)
        logger.info("Scrapy process completed successfully")
    except Exception as e:
        logger.error(f"Error in Scrapy process: {str(e)}")


@require_http_methods(["GET"])
def harvest_listings(request):
    """
    Django view to initiate the harvesting process.

    This view starts a Scrapy spider to harvest listings. It ensures that
    only one harvesting process runs at a time and handles various error
    scenarios.

    Args:
        request (HttpRequest): The incoming request object.

    Returns:
        HttpResponse: A response indicating the status of the harvesting process.
    """
    try:
        if not reactor.running:
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
