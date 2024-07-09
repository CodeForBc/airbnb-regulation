from django.test import TestCase
from django.contrib.contenttypes.models import ContentType
from listings.listing_models import Listing
from policies.models.listing_policy_result_model import ListingPolicyResult
from policies.models.valid_registration_number_policy_model import ValidRegistrationNumberPolicy

class ListingPolicyResultModelTest(TestCase):

    def setUp(self):
        self.listing = Listing.objects.create(name="Test Listing")
        self.policy = ValidRegistrationNumberPolicy.objects.create(name="Test Policy", registration_number="14-123456")

    def test_create_listing_policy_result(self):
        content_type = ContentType.objects.get_for_model(ValidRegistrationNumberPolicy)
        listing_policy_result = ListingPolicyResult.objects.create(
            listing=self.listing,
            content_type=content_type,
            object_id=self.policy.id,
            policy_result=True,
            result_details="Test result details"
        )

        self.assertIsInstance(listing_policy_result, ListingPolicyResult)
        self.assertEqual(listing_policy_result.listing, self.listing)
        self.assertEqual(listing_policy_result.policy, self.policy)
        self.assertEqual(listing_policy_result.policy_result, True)
        self.assertEqual(listing_policy_result.result_details, "Test result details")

    def test_listing_policy_result_str(self):
        content_type = ContentType.objects.get_for_model(ValidRegistrationNumberPolicy)
        listing_policy_result = ListingPolicyResult.objects.create(
            listing=self.listing,
            content_type=content_type,
            object_id=self.policy.id,
            policy_result=True,
            result_details="Test result details"
        )

        expected_str = f'Result {listing_policy_result.id} for listing {self.listing.name} and policy {self.policy.name}'
        self.assertEqual(str(listing_policy_result), expected_str)
