from django.urls import path
from . import views

app_name = "Bookmark"

urlpatterns = [
    path("", views.show_bookmark, name="show_bookmark"),
]