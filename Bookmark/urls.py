from django.urls import path
from Bookmark.views import show_bookmark, toggle_bookmark, update_note

app_name = "Bookmark"

urlpatterns = [
    path("", show_bookmark, name='show_bookmark'),
    path("<uuid:event_id>/", toggle_bookmark, name="toggle_bookmark"),
    path("<uuid:event_id>/note/", update_note, name="update_note"),
]