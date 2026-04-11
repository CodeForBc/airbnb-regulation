from django.urls import path
from . import views

urlpatterns = [
    path("harvest-listings/", views.harvest_listings, name="harvest_listings"),
    path("refresh-listing/<str:airbnb_listing_id>/", views.refresh_listing, name="refresh_listing"),
]
