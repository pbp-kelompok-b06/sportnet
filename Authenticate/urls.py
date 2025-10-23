from django.urls import path
from Authenticate.views import *

app_name = 'Authenticate'

urlpatterns = [
    path('login/', log_in, name='login'),
    path('register/participant1/', register_participant_step1, name='register_participant_step1'),
    path('register/participant2/', register_participant_step2, name='register_participant_step2'),
    path('register/organizer1/', register_organizer_step1,name='register_organizer_step1'),
    path('register/organizer2/', register_organizer_step2,name='register_organizer_step2'),
    path('logout/', log_out, name='logout'),
    path('register/', register_role_selection, name='register_role_selection'),
]