from django.http import HttpResponse
from django.views.decorators.http import require_http_methods
import logging
from .tasks import mock_action, run_harvest_task
import time

# Set up logger for this module
logger = logging.getLogger(__name__)

# Global flag to track if the spider is currently running
is_scraping = False


def with_celery(request):
    res = mock_action.delay()
    return HttpResponse("Celery task is done", status=200)


def without_celery(request):
    time.sleep(15)
    return HttpResponse("Celery task is done", status=200)


def handle_spider_completion():
    """
    Handle actions to perform when the spider completes crawling.
    """
    global is_scraping
    is_scraping = False
    logger.info(f"Scrapy crawl completed and flag reset. Flag: {is_scraping}")
    logger.info("Scrapy process completed successfully")


@require_http_methods(["GET"])
def harvest_listings(request):
    """
       Django view to initiate the harvesting process as a Celery task.
       """
    try:
        # Trigger the Celery task
        run_harvest_task.delay()
        logger.info("Harvesting process started via Celery task")
        return HttpResponse("Harvesting process started", status=202)
    except Exception as e:
        # Log any unexpected errors
        logger.error(f"Failed to start harvesting process: {str(e)}")
        return HttpResponse("Failed to start harvesting process", status=500)
