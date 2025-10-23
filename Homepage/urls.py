from django.urls import path
from Homepage.views import show_main, get_event_data_json # Import view baru

app_name = 'Homepage'

urlpatterns = [
    path('', show_main, name='show_main'),
    # URL baru untuk mengambil data event via AJAX
    path('json/', get_event_data_json, name='get_event_data_json'),
]