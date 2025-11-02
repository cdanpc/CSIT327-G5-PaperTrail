from django.urls import path
from . import views

app_name = "bookmarks"

urlpatterns = [
    path("", views.bookmark_list, name="bookmark_list"),
    path("toggle/<int:resource_id>/", views.toggle_bookmark, name="toggle"),
]
