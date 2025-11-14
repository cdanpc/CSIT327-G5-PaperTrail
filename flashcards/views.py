from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.http import HttpRequest, HttpResponse
import json

from .models import Deck, Card
from .forms import DeckForm, CardForm


@login_required
def deck_list(request: HttpRequest) -> HttpResponse:
    """List decks with optional search & category filter and inline creation."""
    decks = Deck.objects.filter(owner=request.user).prefetch_related("cards")

    # Filters
    q = request.GET.get("q", "").strip()
    category = request.GET.get("category", "").strip()
    if q:
        decks = decks.filter(title__icontains=q) | decks.filter(description__icontains=q)
    if category:
        decks = decks.filter(category=category)

    # Creation
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
            "query": q,
            "selected_category": category,
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
def deck_edit(request: HttpRequest, pk: int) -> HttpResponse:
    """Edit deck title/description/category."""
    deck = get_object_or_404(Deck, pk=pk, owner=request.user)
    if request.method == "POST":
        form = DeckForm(request.POST, instance=deck)
        if form.is_valid():
            form.save()
            return redirect("flashcards:deck_detail", pk=deck.pk)
    else:
        form = DeckForm(instance=deck)
    return render(request, "flashcards/deck_edit.html", {"form": form, "deck": deck})


@login_required
def deck_delete(request: HttpRequest, pk: int) -> HttpResponse:
    """Delete a deck and all its cards (confirmation)."""
    deck = get_object_or_404(Deck, pk=pk, owner=request.user)
    if request.method == "POST":
        deck.delete()
        return redirect("flashcards:deck_list")
    return render(request, "flashcards/deck_delete.html", {"deck": deck})


@login_required
def card_edit(request: HttpRequest, pk: int, card_id: int) -> HttpResponse:
    deck = get_object_or_404(Deck, pk=pk, owner=request.user)
    card = get_object_or_404(Card, pk=card_id, deck=deck)
    if request.method == "POST":
        form = CardForm(request.POST, instance=card)
        if form.is_valid():
            form.save()
            return redirect("flashcards:deck_detail", pk=deck.pk)
    else:
        form = CardForm(instance=card)
    return render(request, "flashcards/card_edit.html", {"form": form, "deck": deck, "card": card})


@login_required
def card_delete(request: HttpRequest, pk: int, card_id: int) -> HttpResponse:
    deck = get_object_or_404(Deck, pk=pk, owner=request.user)
    card = get_object_or_404(Card, pk=card_id, deck=deck)
    if request.method == "POST":
        card.delete()
        return redirect("flashcards:deck_detail", pk=deck.pk)
    return render(request, "flashcards/card_delete.html", {"deck": deck, "card": card})


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
