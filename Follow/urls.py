from django.urls import path
from Follow.views import *

app_name = 'follow'

urlpatterns = [
    path('organizer/<str:username>/followers/', get_organizer_followers, name='get_organizer_followers'),
    path('participant/<str:username>/following/', get_participant_following, name='get_participant_following'),
    path('<int:id_organizer>/follow/', follow_organizer, name='follow_organizer'),
    path('<int:id_organizer>/status/', check_follow_status, name='check_status'),
    path('<int:id_organizer>/unfollow/', unfollow_organizer, name='unfollow_organizer'),
]