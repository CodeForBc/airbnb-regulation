from django.test import TestCase
from policies.models.valid_registration_number_policy_model import ValidRegistrationNumberPolicy
class ValidRegistrationNumberPolicyTest(TestCase):

  def setUp(self):
    # Set up initial data for testing
    self.policy = ValidRegistrationNumberPolicy.objects.create(
        name="Test Policy",
        description="Test Description",
        registration_number="13-123456"  # Valid registration number
    )

  def test_valid_registration_number(self):
    # Test if a valid registration number passes the policy evaluation
    self.assertTrue(self.policy.get_evaluation_result)

  def test_invalid_registration_number(self):
    # Update the policy with an invalid registration number and test
    self.policy.registration_number = "12-123456"  # Invalid registration number (12 is out of range)
    self.policy.save()
    self.assertFalse(self.policy.get_evaluation_result)
    
    self.policy.registration_number = "25-123456"  # Invalid registration number (25 is out of range)
    self.policy.save()
    self.assertFalse(self.policy.get_evaluation_result)
    
    self.policy.registration_number = "20-12345"  # Invalid registration number (only 5 digits)
    self.policy.save()
    self.assertFalse(self.policy.get_evaluation_result)
    
    self.policy.registration_number = "20-1234567"  # Invalid registration number (7 digits)
    self.policy.save()
    self.assertFalse(self.policy.get_evaluation_result)
    
    self.policy.registration_number = "XX-123456"  # Invalid registration number (non-numeric)
    self.policy.save()
    self.assertFalse(self.policy.get_evaluation_result)

  def test_boundary_registration_number(self):
    # Test edge cases for the valid registration number range
    self.policy.registration_number = "13-123456"
    self.policy.save()
    self.assertTrue(self.policy.get_evaluation_result)
    
    self.policy.registration_number = "24-123456"
    self.policy.save()
    self.assertTrue(self.policy.get_evaluation_result)  