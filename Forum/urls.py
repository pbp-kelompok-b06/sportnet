from django.urls import path
from . import views

app_name = 'Forum'

urlpatterns = [
    path('<uuid:event_id>/', views.forum_page_view, name='forum_page'),
    path('edit/<int:post_id>/', views.edit_post_view, name='edit_post'),
    path('delete/<int:post_id>/', views.delete_post_view, name='delete_post'),
    # === API UNTUK FLUTTER ===
    path("api/add/<uuid:event_id>/", views.forum_api_add),
    path("api/list/<uuid:event_id>/", views.forum_api_list),


]
