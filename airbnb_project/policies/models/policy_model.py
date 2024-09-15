from django.db import models
from django.contrib.contenttypes.fields import GenericRelation

class Policy(models.Model):
  """
  Model to store information about a policy.

  Attributes:
      name (CharField): The name of the policy.
      description (CharField): A brief description of the policy.

  Methods:
      __str__(): Returns a string representation of the Policy instance, which is the name of the policy.
  """
  name = models.CharField(max_length=255)
  description = models.CharField(max_length=255)
  listing_policy_result = GenericRelation('ListingPolicyResult')

  class Meta:
    """
    Make this class abstract base class for Policy models
    """
    abstract = True

  def __str__(self) -> str:
    """
    Returns a string representation of the Policy instance.

    Returns:
        str: The name of the policy.
    """
    return self.name

  def evaluate(self) -> bool:
    """
    Abstract method to evaluate the policy
    """
    raise NotImplementedError("Policies must implement this method")