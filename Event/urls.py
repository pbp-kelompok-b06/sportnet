from django.urls import path
from . import views

app_name = "Event"

urlpatterns = [
    path("create/", views.create_event, name="create_event"),
]
