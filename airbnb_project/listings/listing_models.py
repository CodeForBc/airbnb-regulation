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

    # Add a foreign key to the ListingHost model
    host = models.ForeignKey('ListingHost', on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return self.name or 'Listing ' + str(self.airbnb_listing_id)


class ListingHost(models.Model):
    user_id = models.BigIntegerField(unique=True, null=False)  # userId from PassportData
    name = models.CharField(max_length=255, null=True, blank=True)
    title_text = models.CharField(max_length=255, null=True, blank=True)  # titleText from PassportData
    profile_picture_url = models.URLField(null=True, blank=True)  # profilePictureUrl
    thumbnail_url = models.URLField(null=True, blank=True)  # thumbnailUrl
    is_verified = models.BooleanField(default=False)  # isVerified
    is_superhost = models.BooleanField(default=False)  # isSuperhost
    rating_count = models.IntegerField(default=0)  # ratingCount
    rating_average = models.FloatField(default=0.0)  # ratingAverage
    time_as_host_years = models.IntegerField(null=True, blank=True)  # years part of timeAsHost
    time_as_host_months = models.IntegerField(null=True, blank=True)  # months part of timeAsHost

    def __str__(self):
        return self.name or f"Host {self.user_id}"

    @property
    def time_as_host(self):
        return f"{self.time_as_host_years} years and {self.time_as_host_months} months" if self.time_as_host_years and self.time_as_host_months else "Unknown"

