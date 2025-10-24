from django.urls import path
from . import views

app_name = "Event"

urlpatterns = [
    path("create/", views.create_event, name="create_event"),
    path("<uuid:event_id>/", views.event_detail, name="event_detail"),
    path('<uuid:event_id>/join/', views.join_event, name='join'),
    path("<uuid:event_id>/edit/", views.edit_event, name="edit_event"),
    path('book/<uuid:event_id>/', views.book_event, name='book_event'),
]
