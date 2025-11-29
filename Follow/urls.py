from django.urls import path
from Follow.views import *

app_name = 'follow'

urlpatterns = [
    path('<int:id_organizer>/follow/', follow_organizer, name='follow_organizer'),
    path('<int:id_organizer>/unfollow/', unfollow_organizer, name='unfollow_organizer'),
    path('followers/', show_followers, name='show_followers'),
    path('following/', show_following, name='show_following'),
    path('<int:id_organizer>/status/', check_follow_status, name='check_status'),
]