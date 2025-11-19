from django.urls import path
from Homepage.views import show_main, get_event_data_json, ajax_get_events

app_name = 'Homepage'

urlpatterns = [
    path('', show_main, name='show_main'),
    path('json/', get_event_data_json, name='get_event_data_json'),
    path('ajax/events/', ajax_get_events, name='ajax_get_events'),
]