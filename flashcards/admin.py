from django.contrib import admin
from .models import Deck, Card


@admin.register(Deck)
class DeckAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "owner", "cards_count", "last_studied_at", "updated_at")
    list_select_related = ("owner",)
    search_fields = ("title", "owner__username", "owner__first_name", "owner__last_name")


@admin.register(Card)
class CardAdmin(admin.ModelAdmin):
    list_display = ("id", "deck", "short_front", "short_back", "updated_at")
    list_select_related = ("deck",)
    search_fields = ("deck__title", "front_text", "back_text")

    def short_front(self, obj):
        return (obj.front_text[:50] + "...") if len(obj.front_text) > 50 else obj.front_text

    def short_back(self, obj):
        return (obj.back_text[:50] + "...") if len(obj.back_text) > 50 else obj.back_text
