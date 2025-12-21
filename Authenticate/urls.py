from django.urls import path
from Authenticate.views import *

app_name = 'Authenticate'

urlpatterns = [
    path('api/login/', login_api, name='login_api'),
    path('api/register/', register_api, name='register_api'),
    path('api/logout/', logout_api, name='logout_api'),
    path('login/', log_in, name='login'),
    path('logout/', log_out, name='logout'),
    path('register/', register_role_selection, name='register_role_selection'),
    path('register/account/', register, name='register'),
]