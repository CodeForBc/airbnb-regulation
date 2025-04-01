from django.http import HttpResponse
from django.views.decorators.http import require_http_methods
import logging
import datetime
from listings.listing_models import Listing
from policies.services.business_licence_client import BusinessLicenceClient
import json
from policies.models import ListingPolicyResult

# Set up logger for this module
logger = logging.getLogger(__name__)


@require_http_methods(["GET"])
def evaluate_policies(request):
    """
       Django view to initiate the policy evaluation
       """
    try:
        logger.info("Evaluating Listings....")
        unprocessed_items = []
        success_counter = 0
        for listing in Listing.objects.filter(scrapped_at=request.GET['scrapped_at']):
            logger.info(f'listing: {listing}')
            business_licences_number = listing.registration_number
            status = BusinessLicenceClient().get_licence_status(business_licences_number)
            logger.info(f'evaluation status: {status}')
            policy_evaluation_result = True if status.lower() == 'issued' else False
            listing_policy_result = ListingPolicyResult(
            listing=listing,
            policy_result=policy_evaluation_result,
            result_details=business_licences_number,
            result_datetime=datetime.datetime.utcnow())
            # Save the listing to the database
            try:
                logger.info('Trying to save in DB...')
                listing_policy_result.save()
                success_counter += 1
                logger.info(f"{listing.airbnb_listing_id}: evaluated to {policy_evaluation_result} and was saved successfully in DB")
            except Exception as e:
                logger.error(f"Item Id: {listing.airbnb_listing_id} not saved to Policy DB, Full item: {listing_policy_result}, error: {e}")
                unprocessed_items.append(listing_policy_result)
        logger.error(f'All unprocessed Items: {unprocessed_items}')
        return HttpResponse(f"Policy Evaluation Finished - \n Total {success_counter} listings evaluated successfully. Failed: {len(unprocessed_items)}", status=202)
    except Exception as e:
        # Log any unexpected errors
        logger.error(f"Failed to start policy evaluation process: {str(e)}")
        return HttpResponse("Failed to start policy evaluation process", status=500)
