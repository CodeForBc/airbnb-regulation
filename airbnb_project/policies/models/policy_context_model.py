from .policy_models import Policy
from ...listings.listing_models import Listing
from .listing_policy_result_models import ListingPolicyResult

class PolicyContext:
  """
  Context for evaluating policies on a listing and storing the results.

  Attributes:
        listing (Listing): The listing to which the policy is applied.
        policy (Policy): The policy to evaluate.
        policy_results (list): List to store the results of policy evaluations.
  """

  def __init__(self, listing: Listing, policy: Policy) -> None:
    """
    Initialize PolicyContext with a listing and a policy.

    Attribute:
      listing (Listing): The listing to which the policy is applied.
      policy (Policy) : The policy to evaluate listing.
    """

    self._listing = listing
    self._policy = policy
    self.policy_results = []

  @property
  def policy(self) -> Policy:
    """
    Reference to the Policy object.

    Returns:
      Policy: The current policy being evaluated.
    """
    return self._policy

  @policy.setter
  def policy(self, policy: Policy) -> None:
    """
    Setter method to change the Policy object at runtime.

    Args:
      policy (Policy): The new policy to be evaluated.
    """
    self._policy = policy

  def get_policy_result(self) -> None:
    """
    Run evaluate method in a Policy object and append policy, listing and the respective result to list of policy results.
    
    Raises:
      ValueError: If the policy result already exists for the listing.
    """

    if not ListingPolicyResult.objects.filter(listing=self._listing, policy=self._policy).exists():
      result = ListingPolicyResult.objects.create(
        listing = self._listing,
        policy = self._policy,
        policy_result = self._policy.get_evaluation_result(),
        result_details = f"Policy {str(self._policy)} evaluated successfully",
      )
      self.policy_results.append(result)
    else:
      raise ValueError(f"{str(self._policy)} already existed in policy results")

  def get_all_policy_results(self) -> list:
    """
    Get all policy results with policy details and the result.

    Returns:
        list: A list of dictionaries containing policy evaluation results.

    Example:
    [
      {
        'policy': <Policy: Valid Registration Number Policy>,
        'policy_result': True,
        'result_details': 'Policy evaluated successfully.',
        'result_datetime': datetime.datetime(2023, 6, 10, 12, 0)
      },
      {
        'policy': <Policy: Unique Registration Number Policy>,
        'policy_result': False,
        'result_details': 'Policy evaluated successfully.',
        'result_datetime': datetime.datetime(2023, 6, 10, 12, 5)
      }
    ]
    """
    return [
      {
        'policy': result.policy,
        'policy_result': result.policy_result,
        'result_details': result.result_details,
        'result_datetime': result.result_datetime
      }
      for result in ListingPolicyResult.objects.filter(listing=self._listing)
    ]