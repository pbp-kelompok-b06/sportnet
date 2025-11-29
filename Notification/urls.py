from django.urls import path
from Notification.views import show_all, send_event_notification, mark_notification_read, mark_all_read, check_new_notifications, delete_notif



app_name = 'Notification'

urlpatterns = [
    path('', show_all, name='show_all'),
    path('send/<uuid:event_id>/<str:title>/<str:message>/', send_event_notification, name='send_event_notification'),
    path('mark-as-read/<int:notif_id>/', mark_notification_read, name='mark_notification_read'),
    path('mark-all-read/', mark_all_read, name='mark_all_read'),
    path('check-new/', check_new_notifications, name='check_new_notifications'),
    path('delete/<int:notif_id>/', delete_notif, name='delete_notif'),

]