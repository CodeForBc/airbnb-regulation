from django.test import TestCase
from listings.listing_models import Listing
from policies.services.business_licence_client import BusinessLicenceClient

class BusinessLicenceClientTest(TestCase):
  def test_get_licence_status(self):
    client = BusinessLicenceClient()

    issued_listing = Listing(registration_number="24-233482")
    issued_listing_status = client.get_licence_status(issued_listing.registration_number)
    self.assertEqual(issued_listing_status, "Issued")

    pending_listing = Listing(registration_number="24-157245")
    pending_listing_status = client.get_licence_status(pending_listing.registration_number)
    self.assertEqual(pending_listing_status, "Pending")

    cancelled_listing = Listing(registration_number="24-198687")
    cancelled_listing_status = client.get_licence_status(cancelled_listing.registration_number)
    self.assertEqual(cancelled_listing_status, "Cancelled")

    issued_listing_with_two_revisions = Listing(registration_number="24-158492")
    issued_listing_with_two_revisions_status = client.get_licence_status(issued_listing_with_two_revisions.registration_number)
    self.assertEqual(issued_listing_with_two_revisions_status, "Issued")

    gone_out_of_business_listing = Listing(registration_number="24-159005")
    gone_out_of_business_listing_status = client.get_licence_status(gone_out_of_business_listing.registration_number)
    self.assertEqual(gone_out_of_business_listing_status, "Gone Out of Business")