from django.urls import path
from Homepage.views import show_main, get_event_data_json, search_events_ajax

app_name = 'Homepage'

urlpatterns = [
    path('', show_main, name='show_main'),
    # URL baru untuk mengambil data event via AJAX
    path('json/', get_event_data_json, name='get_event_data_json'),
    path('search_ajax/', search_events_ajax, name='search_events_ajax'),
]