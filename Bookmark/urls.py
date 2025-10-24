from django.urls import path
from Bookmark.views import show_bookmark, toggle_bookmark

app_name = "Bookmark"

urlpatterns = [
    path("", show_bookmark, name='show_bookmark'),
    path("<uuid:event_id>/", toggle_bookmark, name="toggle_bookmark"),
]