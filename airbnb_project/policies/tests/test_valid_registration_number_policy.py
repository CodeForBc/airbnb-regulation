from django.test import TestCase
from policies.policies.valid_registration_number_policy import ValidRegistrationNumberPolicy
class ValidRegistrationNumberPolicyTest(TestCase):
  def setUp(self):
    # Create instances of ValidRegistrationNumberPolicy with various registration numbers
    self.policy = ValidRegistrationNumberPolicy(
      name="Valid Registration Policy",
      description="Check if the registration number is valid"
    )
    
  def test_valid_registration_number(self):
    """
    Test valid registration number.
    """
    valid_registration_number="20-123456"
    self.assertTrue(self.policy.get_evaluation_result(valid_registration_number))

  def test_invalid_format_registration_number(self):
    """
    Test invalid format registration number.
    """
    invalid_registration_number="20123456"
    self.assertFalse(self.policy.get_evaluation_result(invalid_registration_number))

  def test_invalid_year_registration_number(self):
    """
    Test invalid year registration number.
    """
    invalid_year_registration_number="12-123456"
    self.assertFalse(self.policy.get_evaluation_result(invalid_year_registration_number))

  def test_empty_registration_number(self):
    """
    Test empty registration number.
    """
    empty_registration_number=""
    self.assertFalse(self.policy.get_evaluation_result(empty_registration_number))

  def test_none_registration_number(self):
    """
    Test None registration number.
    """
    none_registration_number=None
    self.assertFalse(self.policy.get_evaluation_result(none_registration_number))