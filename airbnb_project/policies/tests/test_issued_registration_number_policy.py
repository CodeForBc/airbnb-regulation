from django.test import TestCase
from unittest.mock import patch
from policies.policies.issued_registration_number_policy import IssuedRegistrationNumberPolicy

class IssuedRegistrationNumberPolicyTest(TestCase):
  def setUp(self):
    # Create instances of ValidRegistrationNumberPolicy with various registration numbers
    self.policy = IssuedRegistrationNumberPolicy(
      name="Issued Registration Number Policy",
      description="Check if the registration number is issued in Business Licence"
    )

  @patch('policies.services.business_licence_client.BusinessLicenceClient.get_licence_status')
  def test_issued_registration_number(self, mock_get_licence_status):
    mock_get_licence_status.return_value = "Issued"
    result = self.policy.get_evaluation_result("24-159412")
    self.assertTrue(result)

  @patch('policies.services.business_licence_client.BusinessLicenceClient.get_licence_status')
  def test_not_issued_registration_number(self, mock_get_licence_status):
    mock_get_licence_status.return_value = "Cancelled"
    result = self.policy.get_evaluation_result("24-243792")
    self.assertFalse(result)
