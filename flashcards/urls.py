from django.urls import path
from . import views

app_name = "flashcards"

urlpatterns = [
    path("", views.deck_list, name="deck_list"),
    path("decks/<int:pk>/", views.deck_detail, name="deck_detail"),
    path("decks/<int:pk>/study/", views.study, name="study"),
    path("decks/<int:pk>/edit/", views.deck_edit, name="deck_edit"),
    path("decks/<int:pk>/delete/", views.deck_delete, name="deck_delete"),
    path("decks/<int:pk>/cards/<int:card_id>/edit/", views.card_edit, name="card_edit"),
    path("decks/<int:pk>/cards/<int:card_id>/delete/", views.card_delete, name="card_delete"),
]
