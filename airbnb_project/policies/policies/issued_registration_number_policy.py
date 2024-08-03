from ..models.policy_model import Policy
from ..services.business_licence_client import BusinessLicenceClient

class IssuedRegistrationNumberPolicy(Policy):
  """
  Policy to check if registration number is issued in Business Licences dataset in Vancouver Open Data Portal.
  """
  def __init__(self, *args, **kwargs) -> None:
    super().__init__(*args, **kwargs)
    self.business_licence_client = BusinessLicenceClient()

  def evaluate(self, registration_number: str) -> bool:
    """
    Evaluate the policy on the given registration number.

    Args:
        registration_number (str): The registration number to evaluate.

    Returns:
        bool: True if the registration number is valid, False otherwise.
    """
    result = self.business_licence_client.get_licence_status(registration_number)
    if result == "Issued":
      return True
    return False