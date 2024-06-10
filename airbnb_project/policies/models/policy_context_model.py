from .policy_models import Policy
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
