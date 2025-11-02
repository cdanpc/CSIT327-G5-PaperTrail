from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.http import HttpRequest, HttpResponse
import json

from .models import Deck, Card
from .forms import DeckForm, CardForm


@login_required
def deck_list(request: HttpRequest) -> HttpResponse:
    decks = Deck.objects.filter(owner=request.user).prefetch_related("cards")

    if request.method == "POST":
        form = DeckForm(request.POST)
        if form.is_valid():
            deck: Deck = form.save(commit=False)
            deck.owner = request.user
            deck.save()
            return redirect("flashcards:deck_detail", pk=deck.pk)
    else:
        form = DeckForm()

    return render(
        request,
        "flashcards/deck_list.html",
        {
            "decks": decks,
            "form": form,
        },
    )


@login_required
def deck_detail(request: HttpRequest, pk: int) -> HttpResponse:
    deck = get_object_or_404(Deck, pk=pk, owner=request.user)
    cards = deck.cards.all()

    if request.method == "POST":
        card_form = CardForm(request.POST)
        if card_form.is_valid():
            card: Card = card_form.save(commit=False)
            card.deck = deck
            card.save()
            return redirect("flashcards:deck_detail", pk=deck.pk)
    else:
        card_form = CardForm()

    return render(
        request,
        "flashcards/deck_detail.html",
        {
            "deck": deck,
            "cards": cards,
            "card_form": card_form,
        },
    )


@login_required
def study(request: HttpRequest, pk: int) -> HttpResponse:
    deck = get_object_or_404(Deck, pk=pk, owner=request.user)
    cards = list(
        deck.cards.values("id", "front_text", "back_text")
    )
    cards_json = json.dumps(cards, ensure_ascii=False)

    return render(
        request,
        "flashcards/study.html",
        {
            "deck": deck,
            "cards": cards,
            "cards_json": cards_json,
            "total_cards": len(cards),
        },
    )
