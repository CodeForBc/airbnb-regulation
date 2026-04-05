from django.http import HttpResponse, JsonResponse
from django.views.decorators.http import require_http_methods
import logging
from .tasks import run_harvest_task, run_refresh_single_listing

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


@require_http_methods(["GET"])
def refresh_listing(request, airbnb_listing_id):
    """
    Django view to refresh a single listing's data.
    """
    try:
        run_refresh_single_listing.delay(airbnb_listing_id)
        
        response_data = {
            "status": "success",
            "message": f"Refresh task for {airbnb_listing_id} started",
            "listing_id": airbnb_listing_id
        }
        
        logger.info(f"Refresh task dispatched for listing ID: {airbnb_listing_id}")
        return JsonResponse(response_data, status=202)
    except Exception as e:
        logger.error(f"Failed to start refresh for {airbnb_listing_id}: {str(e)}")
        return JsonResponse({"status": "error", "message": str(e)}, status=500)
