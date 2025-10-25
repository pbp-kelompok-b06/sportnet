from django.urls import path
from Profile.views import *

app_name = 'profile'

urlpatterns = [
    path('', profile_view, name='profile_view'),
    path('edit-profile/', edit_profile, name='edit_profile'),
    path('delete-picture/', delete_Profilepict, name='delete_Profilepict'),
    path('xml/Organizer/', show_xml_Organizer, name='show_xml_Organizer'),
    path('xml/Participant/', show_xml_Participant, name='show_xml_Participant'),
    path('json/Participant/', show_json_Participant, name='show_json_Participant'),
    path('json/Organizer/', show_json_Organizer, name='show_json_Organizer'),
    path('<str:username>/', profile_view, name='profile_view_user'),
]