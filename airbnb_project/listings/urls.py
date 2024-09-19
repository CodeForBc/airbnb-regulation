from django.urls import path
from . import views

urlpatterns = [
    path("scrape-listings/", views.scrape_listings, name="scrape_listings"),
]