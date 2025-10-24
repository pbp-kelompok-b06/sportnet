from django.urls import path
from Dashboard.views import * 

app_name = 'dashboard'

urlpatterns = [
    path('', show, name='show'), 
    path('get-events/', get_organizer_events_json, name='get_organizer_events_json'),
    path('delete-event/<uuid:event_id>/', delete_event, name='delete_event'),
]