from .policy_model import Policy
from listings.listing_models import Listing
from .listing_policy_result_model import ListingPolicyResult

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
    ]from .policy_models import Policy
from .listing_policy_result_models import ListingPolicyResult
class PolicyClient:
  """
  The policy results contain the policy and result of whether it is violated (bool)

  Example:
  [
    {"PolicyA" : True},
    {"PolicyB": False}
  ]
  """

  def __init__(self, policy: Policy) -> None:
    """
    Retrieve results from running a policy

    Attribute:
      policy (Policy) : a method in Policy object
    """

    self.violation_results = []
    self._policy = policy

  @property
  def policy(self) -> Policy:
    """Reference to the Policy object"""
    return self._policy

  @policy.setter
  def policy(self, policy: Policy) -> None:
    """Setter method to change Policy object at runtime"""
    self._policy = policy

  def get_violation_result(self) -> None:
    """
    Run evaluate method in a Policy object
    and append policy name and the result to list of violations
    Returns:
      list[ListingPolicyResult]: A list of ListingPolicyResult objects containing the evaluation results.
    """

    # Use method name (str) in result
    policy_name = str(self._policy)

    # Result includes policy name as key, and the return value of that policy as value
    policy_result = self._policy.get_evaluation_result()

    # Only include violation results if policy name does not exist
    if not any(policy_name in result for result in self.violation_results):
      self.violation_results.append({policy_name: policy_result})
      return
    else:
      raise ValueError(f"{policy_name} already existed in violation results")

  def get_all_violation_results(self) -> list[ListingPolicyResult]:
    """
    Get all violation results with policy name and the result

    Example:
    [
      {'ValidRegistrationNumberPolicy': True},
      {'UniqueRegistrationNumberPolicy': False}
    ]
    """
    return self.violation_results.copy()
