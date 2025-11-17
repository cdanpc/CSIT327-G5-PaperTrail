"""Flashcards domain service helpers.
Encapsulate flashcard-specific querying so dashboard view stays lean.
"""
from django.utils import timezone
from django.db.models import F
from collections import defaultdict
from datetime import timedelta
from typing import List, Dict

from .models import Deck, Card

__all__ = [
    "get_user_deck_ids",
    "get_flashcard_feed_events",
    "get_weekly_flashcard_counts",
    "get_flashcard_summary",
    "get_flashcard_calendar_events",
]

def get_user_deck_ids(user) -> List[int]:
    return list(Deck.objects.filter(owner=user).values_list('id', flat=True))

def get_flashcard_feed_events(user, limit: int = 10) -> List[Dict]:
    """Return flashcard-related feed events (deck create/edit, card add)."""
    events = []
    # Deck creations
    decks_created = Deck.objects.filter(owner=user).order_by('-created_at')[:limit]
    for deck in decks_created:
        events.append({
            'timestamp': deck.created_at,
            'type': 'flashcard_create',
            'icon': 'clone',
            'title': f'Created deck "{deck.title}"',
            'meta': deck.created_at.strftime('%b %d')
        })
    # Card additions
    deck_ids = get_user_deck_ids(user)
    cards_added = Card.objects.filter(deck_id__in=deck_ids).select_related('deck').order_by('-created_at')[:limit]
    for card in cards_added:
        events.append({
            'timestamp': card.created_at,
            'type': 'card_create',
            'icon': 'plus-square',
            'title': f'Added card to "{card.deck.title}"',
            'meta': card.created_at.strftime('%b %d')
        })
    # Deck updates (edits): include only decks whose updated_at is strictly greater
    # than created_at (i.e., they have been modified after creation). Both fields
    # are timezone-aware; no need for make_aware calls.
    deck_updates = Deck.objects.filter(owner=user, updated_at__gt=F('created_at')).order_by('-updated_at')[:limit]
    for deck in deck_updates:
        events.append({
            'timestamp': deck.updated_at,
            'type': 'flashcard_edit',
            'icon': 'edit',
            'title': f'Updated deck "{deck.title}"',
            'meta': deck.updated_at.strftime('%b %d')
        })
    # Sort & slice
    events.sort(key=lambda e: e['timestamp'], reverse=True)
    return events[:limit]

def get_weekly_flashcard_counts(user, date_list: List[timezone.datetime.date]) -> List[int]:
    """Return list of counts of cards created by user for the provided date objects."""
    deck_ids = get_user_deck_ids(user)
    counts = []
    for day in date_list:
        counts.append(Card.objects.filter(deck_id__in=deck_ids, created_at__date=day).count())
    return counts

def get_flashcard_summary(user):
    """Return aggregated counts and recent decks for dashboard summary widgets."""
    total_decks = Deck.objects.filter(owner=user).count()
    total_cards = Card.objects.filter(deck__owner=user).count()
    recent_decks = Deck.objects.filter(owner=user).order_by('-updated_at')[:5]
    last_studied = (
        Deck.objects.filter(owner=user, last_studied_at__isnull=False)
        .order_by('-last_studied_at')
        .first()
    )
    return {
        'total_decks': total_decks,
        'total_cards': total_cards,
        'recent_decks': recent_decks,
        'last_studied_deck': last_studied,
    }

def get_flashcard_calendar_events(user, month: int, year: int) -> Dict[int, List[Dict]]:
    """Return per-day flashcard events for the given month/year."""
    events_by_day = defaultdict(list)
    # Deck creations
    deck_creations = Deck.objects.filter(owner=user, created_at__month=month, created_at__year=year)
    for deck in deck_creations:
        events_by_day[deck.created_at.day].append({'title': f'Created deck: {deck.title}', 'type': 'flashcard_created'})
    # Card creations
    deck_ids = get_user_deck_ids(user)
    card_creations = Card.objects.filter(deck_id__in=deck_ids, created_at__month=month, created_at__year=year).select_related('deck')
    for card in card_creations:
        events_by_day[card.created_at.day].append({'title': f'Added card to {card.deck.title}', 'type': 'card_added'})
    # Study sessions
    deck_studies = Deck.objects.filter(owner=user, last_studied_at__isnull=False, last_studied_at__month=month, last_studied_at__year=year)
    for deck in deck_studies:
        events_by_day[deck.last_studied_at.day].append({'title': f'Studied: {deck.title}', 'type': 'flashcard_study'})
    return dict(events_by_day)
