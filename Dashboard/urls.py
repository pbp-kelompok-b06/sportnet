from django.urls import path
from . import views 

app_name = 'dashboard'

urlpatterns = [
    path('', views.show, name='show'), 
]