from django.db import models
from airbnb_project.listings.listing_models import Listing
from .policy_models import Policy

class ListingPolicyResult(models.Model):
  listing = models.ForeignKey(Listing, on_delete=models.CASCADE)
  policy = models.ForeignKey(Policy, on_delete=models.CASCADE)
  policy_result = models.BooleanField()
  result_details = models.TextField()
  result_datetime = models.DateTimeField()

  def __str__(self):
    return f'Result {self.result_id} for listing {self.airbnb_listing.name} and policy {self.policy.policy_name}'
