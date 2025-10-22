from django.urls import path
from Authenticate.views import *

app_name = 'Authenticate'

urlpatterns = [
    path('login/', log_in, name='login'),
    path('register/participant', register_participant, name='register_participant'),
    path('register/organizer', register_organizer,name='regiseter_organizer'),
    path('logout/', log_out, name='logout'),
]