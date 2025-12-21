from django.urls import path
from . import views

app_name = 'Forum'

urlpatterns = [
    # API UNTUK FLUTTER
    path('api/list/<uuid:event_id>/', views.forum_api_list, name='forum_api_list'),
    path('api/add/<uuid:event_id>/', views.forum_api_add, name='forum_api_add'),
    #
    path('<uuid:event_id>/', views.forum_page_view, name='forum_page'),
    path('edit/<int:post_id>/', views.edit_post_view, name='edit_post'),
    path('delete/<int:post_id>/', views.delete_post_view, name='delete_post'),
    
]
