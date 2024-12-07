from django.http import HttpResponse
from django.views.decorators.http import require_http_methods
import logging
from .tasks import mock_action, run_harvest_task
import time

# Set up logger for this module
logger = logging.getLogger(__name__)


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
