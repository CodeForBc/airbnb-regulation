from django.db import models

class Listing(models.Model):
  name = models.CharField(max_length=100)
  baths = models.CharField(max_length=10)
  beds = models.CharField(max_length=10)
  latitude = models.CharField(max_length=20)
  location = models.CharField(max_length=20)
  longitude = models.CharField(max_length=20)
  person_capacity = models.CharField(max_length=20)
  registration_number = models.CharField(max_length=20)
  room_type = models.CharField(max_length=20)
  title = models.CharField(max_length=100)

  def __str__(self):
    return self.name
