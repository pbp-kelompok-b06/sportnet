from django.urls import path
from . import views

app_name = 'Review'

urlpatterns = [
    path('<uuid:event_id>/', views.review_page_view, name='review_page'),
]
