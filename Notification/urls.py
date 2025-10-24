from django.urls import path
from Notification.views import show_all, send_event_notification

app_name = 'Notification'

urlpatterns = [
    path('', show_all, name='show_all'),
    path('send/<uuid:event_id>/<str:title>/<str:message>/', send_event_notification, name='send_event_notification'),
]