from django.db import models

class Policy(models.Model):
  """
  Model to store information about a policy.

  Attributes:
      name (CharField): The name of the policy.
      description (CharField): A brief description of the policy.

  Methods:
      __str__(): Returns a string representation of the Policy instance, which is the name of the policy.
  """
  name = models.CharField(max_length=100)
  description = models.CharField(max_length=100)

  def __str__(self) -> str:
    """
    Returns a string representation of the Policy instance.

    Returns:
        str: The name of the policy.
    """
    return self.name

  @property
  def get_evaluation_result(self) -> bool:
    """
    Abstract method to evaluate the policy
    """
    pass