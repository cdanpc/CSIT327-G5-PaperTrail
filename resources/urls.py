from django.urls import path
from . import views

app_name = 'resources'

urlpatterns = [
    # Home Page (Catch-all for base URL)
    path('', views.home, name='home'),
]