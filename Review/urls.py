from django.urls import path
from . import views

app_name = 'Review'

urlpatterns = [
    # === API FOR FLUTTER ===
    path('api/list/<uuid:event_id>/', views.review_api_list, name='review_api_list'),
    path("api/add/<uuid:event_id>/", views.review_api_add),
    #
    path('<uuid:event_id>/', views.review_page_view, name='review_page'),
    path('edit/<int:review_id>/', views.edit_review_view, name='edit_review'),
    path('delete/<int:review_id>/', views.delete_review_view, name='delete_review'),
    
    

]
