from django.db import models
from django.utils import timezone

class Listing(models.Model):
    airbnb_listing_id = models.TextField(blank=False, null=False)
    name = models.TextField(null=True, blank=True)
    baths = models.FloatField(null=True, blank=True)
    beds = models.FloatField(null=True, blank=True)
    latitude = models.TextField(null=True, blank=True)
    location = models.TextField(null=True, blank=True)
    longitude = models.TextField(null=True, blank=True)
    person_capacity = models.IntegerField(null=True, blank=True)
    registration_number = models.TextField(null=True, blank=True)
    room_type = models.TextField(null=True, blank=True)
    title = models.TextField(null=True, blank=True)
    is_bath_shared = models.BooleanField(null=True, blank=True)
    baths_text = models.TextField(null=True, blank=True)
    scrapped_at = models.DateField(null=True, blank=True, default=timezone.now)

    def __str__(self):
        return self.name
