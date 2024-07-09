from django.db import models
from .policy_model import Policy

import re

class ValidRegistrationNumberPolicy(Policy):
  registration_number = models.CharField(max_length=20)

  def is_valid_registration_number(self) -> bool:
    if self.registration_number is None or self.registration_number == "":
      return False
    
    valid_registration_pattern = re.compile(r"^[0-9]{2}-[0-9]{6}$")
    START_YEAR = 13
    END_YEAR = 24

    if valid_registration_pattern.match(self.registration_number):
        registration_year = int(self.registration_number[0:2])
        if registration_year > END_YEAR or registration_year < START_YEAR:
            return False
        else:
            return True
    else:
        return False
    
  @property
  def get_evaluation_result(self) -> bool:
    return self.is_valid_registration_number()