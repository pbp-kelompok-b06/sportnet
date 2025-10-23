from django.urls import path
from . import views  # Impor views dari app forum

app_name = 'forum' # Namespace agar tidak bentrok

urlpatterns = [

    path(
        'event/<int:event_id>/', 
        views.forum_page_view, 
        name='forum_page' 
    ),
]