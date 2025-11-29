from django.urls import path
from Homepage.views import show_main, get_event_data_json, search_events_ajax, proxy_image

app_name = 'Homepage'

urlpatterns = [
    path('', show_main, name='show_main'),
    path('json/', get_event_data_json, name='get_event_data_json'),
    path('search_ajax/', search_events_ajax, name='search_events_ajax'),
    path('proxy-image/', proxy_image, name='proxy_image'),
]
