from ..models.policy_model import Policy
import re

class ValidRegistrationNumberPolicy(Policy):
  """
  Policy to check if the registration number is valid based on a specific pattern and year range.
  """
  
  START_YEAR = 13
  END_YEAR = 24
  VALID_REGISTRATION_PATTERN = re.compile(r"^[0-9]{2}-[0-9]{6}$")
  
  def is_valid_registration_number(self, registration_number: str) -> bool:
    """
    Validate the registration number based on pattern and year range.

    Args:
        registration_number (str): The registration number to validate.

    Returns:
        bool: True if the registration number is valid, False otherwise.
    """
    if not registration_number:
      return False

    if self.VALID_REGISTRATION_PATTERN.match(registration_number):
      registration_year = int(registration_number[0:2])
      return self.START_YEAR <= registration_year <= self.END_YEAR
    else:
      return False
    
  def evaluate(self, registration_number: str) -> bool:
    """
    Evaluate the policy on the given registration number.

    Args:
        registration_number (str): The registration number to evaluate.

    Returns:
        bool: True if the registration number is valid, False otherwise.
    """
    return self.is_valid_registration_number(registration_number)