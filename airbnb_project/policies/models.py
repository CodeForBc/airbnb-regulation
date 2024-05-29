from django.db import models

class Policy(models.Model):
  name = models.CharField(max_length=100)
  description = models.CharField(max_length=100)

  def __str__(self):
    return self.policy_name
