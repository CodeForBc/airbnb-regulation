from django.urls import path
from . import views

urlpatterns = [
    path("harvest-listings/", views.harvest_listings, name="harvest_listings"),
]