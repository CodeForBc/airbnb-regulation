from django.urls import path
from . import views

urlpatterns = [
    path("harvest-listings/", views.harvest_listings, name="harvest_listings"),
    path("with-celery/", views.with_celery, name="with_celery"),
    path("without-celery/", views.without_celery, name="without_celery"),
]
