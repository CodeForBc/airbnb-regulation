from ..models.policy_model import Policy
from ..services.business_licence_client import BusinessLicenceClient

class IssuedRegistrationNumberPolicy(Policy):
  def __init__(self, name, description) -> None:
    super().__init__(name, description)
    self.business_licence_client = BusinessLicenceClient()

  def get_evaluation_result(self, registration_number: str) -> bool:
    result = self.business_licence_client.get_licence_status(registration_number)
    if result == "Issued":
      return True
    return False