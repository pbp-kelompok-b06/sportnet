from django.urls import path
from . import views  # Impor views dari app review

app_name = 'review' # Namespace agar tidak bentrok

urlpatterns = [
    
    path(
        'event/<int:event_id>/add/', 
        views.add_review_view, 
        name='add_review'
    ),
]