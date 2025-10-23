from django.urls import path
from Bookmark.views import show_main

app_name = 'Bookmark'

urlpatterns = [
    path('', show_main, name='show_main'),

]