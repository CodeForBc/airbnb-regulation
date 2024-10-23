from django.db import models

class Listing(models.Model):
    airbnb_listing_id = models.TextField(blank=False, null=False)
    name = models.TextField(null=True, blank=True)
    baths = models.TextField(null=True, blank=True)
    beds = models.TextField(null=True, blank=True)
    latitude = models.TextField(null=True, blank=True)
    location = models.TextField(null=True, blank=True)
    longitude = models.TextField(null=True, blank=True)
    person_capacity = models.TextField(null=True, blank=True)
    registration_number = models.TextField(null=True, blank=True)
    room_type = models.TextField(null=True, blank=True)
    title = models.TextField(null=True, blank=True)
    is_bath_shared = models.BooleanField(null=True, blank=True)
    baths_text = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.name
