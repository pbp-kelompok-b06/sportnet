from django.urls import path
from Bookmark.views import show_bookmark

app_name = "Bookmark"

urlpatterns = [
    path("", show_bookmark, name='show_bookmark'),
]