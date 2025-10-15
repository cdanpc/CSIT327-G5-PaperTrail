from django.urls import path
from . import views

app_name = 'resources'

urlpatterns = [
    # Home Page (Catch-all for base URL)
    path('', views.home, name='home'),
    
    # Resource CRUD
    path('list/', views.resource_list, name='resource_list'),
    path('upload/', views.resource_upload, name='resource_upload'),
    path('<int:pk>/', views.resource_detail, name='resource_detail'),
    path('<int:pk>/edit/', views.resource_edit, name='resource_edit'),
    path('<int:pk>/delete/', views.resource_delete, name='resource_delete'),
    path('<int:pk>/download/', views.resource_download, name='resource_download'),
]