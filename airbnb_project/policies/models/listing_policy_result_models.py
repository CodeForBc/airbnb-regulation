from django.db import models
from listings.listing_models import Listing
from policies.models.policy_models import Policy

class ListingPolicyResult(models.Model):
  """
  Model to store the result of a policy evaluation on a listing.

  Attributes:
      listing (ForeignKey): Reference to the Listing model instance.
      policy (ForeignKey): Reference to the Policy model instance.
      policy_result (BooleanField): The result of the policy evaluation (True if the listing complies with the policy, False otherwise).
      result_details (TextField): Additional details about the policy check result.
      result_datetime (DateTimeField): The date and time when the policy evaluation result was recorded/updated.

  Methods:
      __str__(): Returns a string representation of the ListingPolicyResult instance, indicating the result ID, listing name, and policy name.
  """
  listing = models.ForeignKey(Listing, on_delete=models.CASCADE)
  policy = models.ForeignKey(Policy, on_delete=models.CASCADE)
  policy_result = models.BooleanField()
  result_details = models.TextField()
  result_datetime = models.DateTimeField(auto_now_add=True, auto_now=True)

  def __str__(self):
    """
    Returns a string representation of the ListingPolicyResult instance.

    Returns:
        str: A string indicating the result ID, listing name, and policy name.
    """
    return f'Result {self.result_id} for listing {self.airbnb_listing.name} and policy {self.policy.policy_name}'
