from django.urls import path
from . import views

app_name = 'Forum'

urlpatterns = [
    path('<uuid:event_id>/', views.forum_page_view, name='forum_page'),
]
