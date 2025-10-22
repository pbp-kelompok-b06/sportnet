from django.urls import path
from Notification.views import show_all

app_name = 'Notification'

urlpatterns = [
    path('', show_all, name='show_all'),
]