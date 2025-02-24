from django.urls import path
from . import views

urlpatterns = [
    path("evaluate-policies/", views.evaluate_policies, name="evaluate_policies"),
]
