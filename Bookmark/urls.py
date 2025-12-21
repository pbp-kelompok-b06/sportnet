from django.urls import path
from . import views

app_name = "Bookmark"

urlpatterns = [
    # dipakai JS (card_event.js)
    path("<uuid:event_id>/", views.toggle_bookmark, name="toggle_bookmark"),

    # dipakai halaman bookmarks.html (note form)
    path("update-note/<uuid:event_id>/", views.update_note, name="update_note"),
    path("", views.show_bookmark, name="show_bookmark"),

    # endpoint khusus Flutter
    path("api/bookmarks/", views.api_list_bookmarks, name="api_list_bookmarks"),
    path("api/bookmarks/note/<uuid:event_id>/", views.api_update_note, name="api_update_note"),
    path("api/bookmarks/toggle/<uuid:event_id>/", views.api_toggle_bookmark, name="api_toggle_bookmark"),
]