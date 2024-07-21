from django.test import TestCase
from unittest.mock import MagicMock
from django.contrib.contenttypes.models import ContentType
from listings.listing_models import Listing
from policies.models.policy_model import Policy
from policies.models.listing_policy_result_model import ListingPolicyResult
class ListingPolicyResultModelTest(TestCase):
  def setUp(self):
    # Create a mock instance of Listing
    self.mock_listing = MagicMock(spec=Listing)
    self.mock_listing.id = 1
    self.mock_listing.name = 'Test Listing'
    self.mock_listing._state = MagicMock()

    # Create a mock instance of a policy
    self.mock_policy = MagicMock(spec=Policy)
    self.mock_policy.id = 1
    self.mock_policy.name = 'Test Policy'
    self.mock_policy._state = MagicMock()
    
    # Create a mock instance of ContentType
    self.mock_policy_content_type = MagicMock(spec=ContentType)
    self.mock_policy_content_type.id = 1
    self.mock_policy_content_type._state = MagicMock()
    self.mock_policy_content_type._state.db = None

    # Patch the ContentType.objects.get_for_model method to return the mock policy content type
    self.mock_get_for_model = MagicMock(return_value=self.mock_policy_content_type)
    ContentType.objects.get_for_model = self.mock_get_for_model

    self.mock_listing_policy_result = ListingPolicyResult(
      listing=self.mock_listing,
      content_type=self.mock_policy_content_type,
      policy=self.mock_policy,
      policy_result=True,
      result_details='Policy evaluated successfully.',
      result_datetime='2023-07-08T12:00:00Z'
    )
    self.mock_listing_policy_result.object_id = self.mock_policy.id
  
  def test_create_listing_policy_result(self):
    self.assertIsInstance(self.mock_listing_policy_result, ListingPolicyResult)
    self.assertEqual(self.mock_listing_policy_result.listing, self.mock_listing)
    self.assertEqual(self.mock_listing_policy_result.content_type, self.mock_policy_content_type)
    self.assertEqual(self.mock_listing_policy_result.object_id, self.mock_policy.id)
    self.assertEqual(self.mock_listing_policy_result.policy_result, True)
    self.assertEqual(self.mock_listing_policy_result.result_details, 'Policy evaluated successfully.')
    self.assertEqual(self.mock_listing_policy_result.result_datetime, '2023-07-08T12:00:00Z')
