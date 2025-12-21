from django.urls import path
from Dashboard.views import * 

app_name = 'dashboard'

urlpatterns = [
    path('', show, name='show'), 
    path('get-organizer-events-json/', get_organizer_events_json, name='get_organizer_events_json'),
    path('delete-event/<uuid:event_id>/', delete_event, name='delete_event'),
    # pinned API
    path("api/pins/", api_list_pins, name="api_list_pins"),
    path("api/pins/toggle/<uuid:event_id>/", api_toggle_pin, name="api_toggle_pin"),
    path("api/pins/move/<uuid:event_id>/", api_move_pin, name="api_move_pin"),
]