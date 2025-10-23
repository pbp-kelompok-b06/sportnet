from django.urls import path
from Profile.views import show_main, edit_profile

app_name = 'Profile'

urlpatterns = [
    path('', show_main, name='show_main'),
    path('edit/', edit_profile, name='edit_profile'),
]