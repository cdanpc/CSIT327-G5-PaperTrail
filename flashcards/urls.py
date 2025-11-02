from django.urls import path
from . import views

app_name = "flashcards"

urlpatterns = [
    path("", views.deck_list, name="deck_list"),
    path("decks/<int:pk>/", views.deck_detail, name="deck_detail"),
    path("decks/<int:pk>/study/", views.study, name="study"),
]
