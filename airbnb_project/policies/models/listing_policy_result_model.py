from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from listings.listing_models import Listing

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
  content_type = models.ForeignKey(ContentType, null=True, on_delete=models.CASCADE)
  object_id = models.PositiveIntegerField(null=True)
  policy = GenericForeignKey('content_type', 'object_id')
  policy_result = models.BooleanField()
  result_details = models.TextField()
  result_datetime = models.DateTimeField(auto_now_add=True)
