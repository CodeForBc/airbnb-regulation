from django.test import TestCase
from policies.services.business_licence_client import BusinessLicenceClient

class BusinessLicenceClientTest(TestCase):
  def test_get_licence_status(self):
    client = BusinessLicenceClient()

    issued_listing_status = client.get_licence_status("24-233482")
    self.assertEqual(issued_listing_status, "Issued")

    pending_listing_status = client.get_licence_status("24-157245")
    self.assertEqual(pending_listing_status, "Pending")

    cancelled_listing_status = client.get_licence_status("24-198687")
    self.assertEqual(cancelled_listing_status, "Cancelled")

    issued_listing_with_two_revisions_status = client.get_licence_status("24-158492")
    self.assertEqual(issued_listing_with_two_revisions_status, "Issued")

    gone_out_of_business_listing_status = client.get_licence_status("24-159005")
    self.assertEqual(gone_out_of_business_listing_status, "Gone Out of Business")