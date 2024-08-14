from django.test import TestCase
from policies.models.valid_registration_number_policy_model import ValidRegistrationNumberPolicy
class ValidRegistrationNumberPolicyTest(TestCase):
  def setUp(self):
    # Create instances of ValidRegistrationNumberPolicy with various registration numbers
    self.valid_policy = ValidRegistrationNumberPolicy(registration_number="20-123456")
    self.invalid_format_policy = ValidRegistrationNumberPolicy(registration_number="20123456")
    self.invalid_year_policy = ValidRegistrationNumberPolicy(registration_number="12-123456")
    self.empty_policy = ValidRegistrationNumberPolicy(registration_number="")
    self.none_policy = ValidRegistrationNumberPolicy(registration_number=None)
  
  def test_valid_registration_number(self):
    """
    Test valid registration number.
    """
    self.assertTrue(self.valid_policy.get_evaluation_result)

  def test_invalid_format_registration_number(self):
    """
    Test invalid format registration number.
    """
    self.assertFalse(self.invalid_format_policy.get_evaluation_result)

  def test_invalid_year_registration_number(self):
    """
    Test invalid year registration number.
    """
    self.assertFalse(self.invalid_year_policy.get_evaluation_result)

  def test_empty_registration_number(self):
    """
    Test empty registration number.
    """
    self.assertFalse(self.empty_policy.get_evaluation_result)

  def test_none_registration_number(self):
    """
    Test None registration number.
    """
    self.assertFalse(self.none_policy.get_evaluation_result)