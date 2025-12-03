from django.urls import path
from . import views

app_name = "flashcards"

urlpatterns = [
    path("", views.deck_list, name="deck_list"),
    path("create/", views.deck_create, name="deck_create"),
    path("<int:pk>/", views.deck_detail, name="deck_detail"),
    path("<int:pk>/edit/", views.deck_edit, name="deck_edit"),
    path("<int:pk>/delete/", views.deck_delete, name="deck_delete"),
    path("<int:pk>/study/", views.study, name="study"),
    path("<int:pk>/bookmark/", views.toggle_bookmark, name="bookmark_toggle"),
    path("<int:pk>/cards/<int:card_id>/edit/", views.card_edit, name="card_edit"),
    path("<int:pk>/cards/<int:card_id>/delete/", views.card_delete, name="card_delete"),
    path("<int:pk>/rate/", views.rate_deck, name="rate_deck"),
    path("<int:pk>/comment/add/", views.add_deck_comment, name="add_deck_comment"),
    path("<int:pk>/comment/<int:comment_id>/delete/", views.delete_deck_comment, name="delete_deck_comment"),
    # AJAX Updates
    path("<int:pk>/update-title/", views.update_deck_title, name="update_deck_title"),
    path("<int:pk>/cards/<int:card_id>/update/", views.update_card, name="update_card"),
    # Moderation
    path("moderation/", views.deck_moderation_list, name="deck_moderation_list"),
    path("moderation/approve/<int:pk>/", views.approve_deck, name="approve_deck"),
    path("moderation/reject/<int:pk>/", views.reject_deck, name="reject_deck"),
    path("moderation/bulk-verify/", views.bulk_verify_decks, name="bulk_verify_decks"),
]
