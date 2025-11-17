from django.urls import path
from . import views

app_name = 'resources'

urlpatterns = [
    # Home Page (Catch-all for base URL)
    path('', views.home, name='home'),
    
    # Resource CRUD
    path('list/', views.resource_list, name='resource_list'),
    path('api/list/', views.resource_list_api, name='resource_list_api'),
    path('my-resources/', views.my_resources, name='my_resources'),
    path('upload/', views.resource_upload, name='resource_upload'),
    path('<int:pk>/', views.resource_detail, name='resource_detail'),
    path('<int:pk>/edit/', views.resource_edit, name='resource_edit'),
    path('<int:pk>/delete/', views.resource_delete, name='resource_delete'),
    path('<int:pk>/download/', views.resource_download, name='resource_download'),
    
    # Rating and Comments
    path('<int:pk>/rate/', views.rate_resource, name='rate_resource'),
    path('<int:pk>/comment/', views.add_comment, name='add_comment'),
    path('comment/<int:pk>/delete/', views.delete_comment, name='delete_comment'),

    # Moderation
    path('moderation/', views.moderation_list, name='moderation_list'),
    path('moderation/<int:pk>/approve/', views.approve_resource, name='approve_resource'),
    path('moderation/<int:pk>/reject/', views.reject_resource, name='reject_resource'),
    path('verified/', views.verified_resources_list, name='verified_resources_list'),
]