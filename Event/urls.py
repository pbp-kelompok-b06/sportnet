from django.urls import path
from . import views

app_name = "Event"

urlpatterns = [
    path("create/", views.create_event, name="create_event"),
    path("<uuid:event_id>/", views.event_detail, name="event_detail"),
    path('<uuid:event_id>/join/', views.join_event, name='join'),
    path("<uuid:event_id>/edit/", views.edit_event, name="edit_event"),
    path('api/<uuid:event_id>/join/', views.join_event_json, name='join_event_json'),
    path('create-flutter/', views.create_event_flutter, name='create_event_flutter'),
    path("json/", views.show_json, name="show_json"),
    path("json/<uuid:event_id>/", views.show_event_by_id_json, name="show_event_by_id_json"),
    path('delete-flutter/<uuid:event_id>/', views.delete_event_flutter, name='delete_event_flutter'),
    path('edit-flutter/<uuid:event_id>/', views.edit_event_flutter, name='edit_event_flutter'),
]
