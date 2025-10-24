from django.urls import path
from Homepage.views import show_main, get_event_data_json, search_events_ajax

app_name = 'Homepage'

urlpatterns = [
    path('', show_main, name='show_main'),
    # URL baru untuk mengambil data event via AJAX (JSON)
    path('json/', get_event_data_json, name='get_event_data_json'),
    # AJAX endpoint that returns HTML fragment for filtered events
    path('search/async/', search_events_ajax, name='search_events_ajax'),
]