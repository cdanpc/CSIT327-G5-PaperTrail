from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.utils import timezone
from django.db.models import Q
import json

from .models import Deck, Card, DeckRating, DeckComment
from django.contrib import messages
from django.core.mail import send_mail
from django.views.decorators.http import require_http_methods
from .forms import DeckForm, CardForm, DeckCommentForm


@login_required
def deck_list(request: HttpRequest) -> HttpResponse:
    """List decks with optional search & category filter and All/My scopes.

    - All: public decks from all users
    - My: user's own decks (any visibility)
    """
    scope = request.GET.get('scope', 'all')
    if scope == 'mine':
        decks = Deck.objects.filter(owner=request.user).prefetch_related("cards")
    else:
        decks = Deck.objects.filter(visibility='public', verification_status='verified').prefetch_related("cards")

    # Filters
    q = request.GET.get("q", "").strip()
    category = request.GET.get("category", "").strip()
    if q:
        decks = decks.filter(Q(title__icontains=q) | Q(description__icontains=q))
    if category:
        decks = decks.filter(category=category)

    return render(
        request,
        "flashcards/deck_list.html",
        {
            "decks": decks,
            "query": q,
            "selected_category": category,
            "scope": scope,
        },
    )


@login_required
def deck_create(request: HttpRequest) -> HttpResponse:
    """Create a new deck."""
    if request.method == "POST":
        form = DeckForm(request.POST)
        if form.is_valid():
            deck: Deck = form.save(commit=False)
            deck.owner = request.user
            # Verification workflow (parity with quizzes/resources)
            if deck.visibility == 'public':
                if getattr(request.user, 'is_professor', False) or request.user.is_staff:
                    deck.verification_status = 'verified'
                    deck.verification_by = request.user
                    deck.verified_at = timezone.now()
                else:
                    deck.verification_status = 'pending'
                    deck.verification_by = None
                    deck.verified_at = None
            else:  # private decks auto-verify
                deck.verification_status = 'verified'
                deck.verification_by = request.user
                deck.verified_at = timezone.now()
            deck.save()
            return redirect("flashcards:deck_detail", pk=deck.pk)
    else:
        form = DeckForm()
    return render(request, "flashcards/deck_create.html", {"form": form})


@login_required
def deck_detail(request: HttpRequest, pk: int) -> HttpResponse:
    deck = get_object_or_404(Deck, pk=pk)
    # Privacy: Only owner can view private decks
    if deck.visibility == 'private' and deck.owner != request.user:
        from django.contrib import messages
        messages.error(request, 'This deck is private.')
        return redirect('flashcards:deck_list')
    # Pending public decks only visible to owner or staff/professors
    if deck.visibility == 'public' and deck.verification_status != 'verified' and deck.owner != request.user and not (getattr(request.user, 'is_professor', False) or request.user.is_staff):
        from django.contrib import messages
        messages.error(request, 'This deck is not yet verified.')
        return redirect('flashcards:deck_list')
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

    # Feedback context (ratings/comments)
    user_rating = None
    comments = []
    try:
        user_rating = DeckRating.objects.filter(user=request.user, deck=deck).first()
    except Exception:
        user_rating = None
    try:
        comments = deck.comments.select_related("user").all()
    except Exception:
        comments = []

    return render(
        request,
        "flashcards/deck_detail.html",
        {
            "deck": deck,
            "cards": cards,
            "card_form": card_form,
            "user_rating": user_rating,
            "comments": comments,
        },
    )


@login_required
def deck_edit(request: HttpRequest, pk: int) -> HttpResponse:
    """Edit deck title/description/category."""
    deck = get_object_or_404(Deck, pk=pk, owner=request.user)
    if request.method == "POST":
        form = DeckForm(request.POST, instance=deck)
        if form.is_valid():
            deck = form.save(commit=False)
            original_visibility = Deck.objects.get(pk=deck.pk).visibility
            new_visibility = deck.visibility
            if new_visibility == 'public':
                if getattr(request.user, 'is_professor', False) or request.user.is_staff:
                    deck.verification_status = 'verified'
                    deck.verification_by = request.user
                    deck.verified_at = timezone.now()
                else:
                    # Student making public: pending unless already verified
                    if deck.verification_status != 'verified':
                        deck.verification_status = 'pending'
                        deck.verification_by = None
                        deck.verified_at = None
            else:  # private
                if deck.verification_status != 'verified':
                    deck.verification_status = 'verified'
                if deck.verification_by is None:
                    deck.verification_by = request.user
                if deck.verified_at is None:
                    deck.verified_at = timezone.now()
            deck.save()
            return redirect("flashcards:deck_detail", pk=deck.pk)
    else:
        form = DeckForm(instance=deck)
    return render(request, "flashcards/deck_edit.html", {"form": form, "deck": deck})


@login_required
def deck_delete(request: HttpRequest, pk: int) -> HttpResponse:
    """Delete a deck and all its cards. POST only; returns 405 otherwise."""
    deck = get_object_or_404(Deck, pk=pk, owner=request.user)
    if request.method != "POST":
        from django.http import HttpResponseNotAllowed
        return HttpResponseNotAllowed(["POST"])
    deck.delete()
    return redirect("flashcards:deck_list")


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
    if request.method != "POST":
        from django.http import HttpResponseNotAllowed
        return HttpResponseNotAllowed(["POST"])
    card.delete()
    return redirect("flashcards:deck_detail", pk=deck.pk)


@login_required
def study(request: HttpRequest, pk: int) -> HttpResponse:
    deck = get_object_or_404(Deck, pk=pk)
    # Privacy: Only owner can study private decks
    if deck.visibility == 'private' and deck.owner != request.user:
        from django.contrib import messages
        messages.error(request, 'This deck is private.')
        return redirect('flashcards:deck_list')
    # Mark last studied timestamp
    deck.mark_studied()
    deck.save(update_fields=["last_studied_at", "updated_at"])
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


@login_required
def toggle_bookmark(request: HttpRequest, pk: int) -> HttpResponse:
    """Toggle bookmark status for deck. Supports AJAX JSON or redirect fallback."""
    deck = get_object_or_404(Deck, pk=pk, owner=request.user)
    deck.is_bookmarked = not deck.is_bookmarked
    deck.save(update_fields=["is_bookmarked", "updated_at"])
    if request.headers.get("x-requested-with") == "XMLHttpRequest":
        return JsonResponse({"bookmarked": deck.is_bookmarked})
    return redirect("flashcards:deck_list")


@login_required
def rate_deck(request: HttpRequest, pk: int) -> HttpResponse:
    deck = get_object_or_404(Deck, pk=pk)
    if deck.owner == request.user:
        from django.contrib import messages
        messages.error(request, 'You cannot rate your own deck.')
        return redirect('flashcards:deck_detail', pk=pk)
    if deck.visibility != 'public' or deck.verification_status != 'verified':
        from django.contrib import messages
        messages.error(request, 'You can only rate public decks.')
        return redirect('flashcards:deck_detail', pk=pk)
    if request.method == 'POST':
        stars = request.POST.get('stars')
        if not stars:
            from django.contrib import messages
            messages.error(request, 'Please select a rating.')
            return redirect('flashcards:deck_detail', pk=pk)
        try:
            stars_int = int(stars)
            if stars_int < 1 or stars_int > 5:
                raise ValueError()
        except ValueError:
            from django.contrib import messages
            messages.error(request, 'Invalid rating value.')
            return redirect('flashcards:deck_detail', pk=pk)
        rating, created = DeckRating.objects.get_or_create(user=request.user, deck=deck, defaults={'stars': stars_int})
        if not created:
            rating.stars = stars_int
            rating.save()
        from django.contrib import messages
        messages.success(request, f'You rated "{deck.title}" with {stars_int} star' + ('s' if stars_int != 1 else '') + '!')
    return redirect('flashcards:deck_detail', pk=pk)


@login_required
def add_deck_comment(request: HttpRequest, pk: int) -> HttpResponse:
    deck = get_object_or_404(Deck, pk=pk)
    if deck.owner == request.user:
        from django.contrib import messages
        messages.error(request, 'You cannot comment on your own deck.')
        return redirect('flashcards:deck_detail', pk=pk)
    if deck.visibility != 'public' or deck.verification_status != 'verified':
        from django.contrib import messages
        messages.error(request, 'You can only comment on public decks.')
        return redirect('flashcards:deck_detail', pk=pk)
    if request.method == 'POST':
        form = DeckCommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.user = request.user
            comment.deck = deck
            comment.save()
            from django.contrib import messages
            messages.success(request, 'Comment added successfully!')
        else:
            from django.contrib import messages
            messages.error(request, 'Error adding comment.')
    return redirect('flashcards:deck_detail', pk=pk)


@login_required
def delete_deck_comment(request: HttpRequest, pk: int, comment_id: int) -> HttpResponse:
    deck = get_object_or_404(Deck, pk=pk)
    comment = get_object_or_404(DeckComment, pk=comment_id, deck=deck)
    if comment.user != request.user:
        from django.contrib import messages
        messages.error(request, 'You can only delete your own comments.')
        return redirect('flashcards:deck_detail', pk=pk)
    if request.method == 'POST':
        comment.delete()
        from django.contrib import messages
        messages.success(request, 'Comment deleted successfully.')
    return redirect('flashcards:deck_detail', pk=pk)


@login_required
def deck_moderation_list(request: HttpRequest) -> HttpResponse:
    """List pending public decks for verification (professors/staff only)."""
    if not (getattr(request.user, 'is_professor', False) or request.user.is_staff):
        messages.error(request, 'You do not have permission to access moderation.')
        return redirect('flashcards:deck_list')
    pending_decks = Deck.objects.filter(visibility='public', verification_status='pending').order_by('-created_at')
    return render(request, 'flashcards/moderation_list.html', {'pending_decks': pending_decks})


@login_required
@require_http_methods(["POST"])
def approve_deck(request: HttpRequest, pk: int) -> HttpResponse:
    """Approve a single deck (professor/staff only)."""
    if not (getattr(request.user, 'is_professor', False) or request.user.is_staff):
        messages.error(request, 'Permission denied.')
        return redirect('flashcards:deck_list')
    deck = get_object_or_404(Deck, pk=pk)
    if deck.verification_status == 'verified':
        messages.info(request, 'Deck already verified.')
        return redirect('flashcards:deck_moderation_list')
    deck.verification_status = 'verified'
    deck.verification_by = request.user
    deck.verified_at = timezone.now()
    deck.save(update_fields=['verification_status', 'verification_by', 'verified_at'])
    # Notify owner via email
    owner = deck.owner
    if getattr(owner, 'email_notifications', False) and getattr(owner, 'email', ''):
        try:
            send_mail(
                subject='Your deck has been verified',
                message=f'Your deck "{deck.title}" is now verified and visible in All Decks.',
                from_email=None,
                recipient_list=[owner.email],
                fail_silently=True,
            )
        except Exception:
            pass
    messages.success(request, f'"{deck.title}" verified successfully.')
    return redirect('flashcards:deck_moderation_list')


# Deck rejection view for moderation
@login_required
@require_http_methods(["POST"])
def reject_deck(request: HttpRequest, pk: int) -> HttpResponse:
    """Reject a single deck (professor/staff only)."""
    if not (getattr(request.user, 'is_professor', False) or request.user.is_staff):
        messages.error(request, 'Permission denied.')
        return redirect('flashcards:deck_list')
    deck = get_object_or_404(Deck, pk=pk)
    if deck.verification_status == 'rejected':
        messages.info(request, 'Deck already rejected.')
        return redirect('flashcards:deck_moderation_list')
    reason = request.POST.get('reason', '').strip()
    deck.verification_status = 'rejected'
    deck.verification_by = request.user
    deck.verified_at = timezone.now()
    deck.save(update_fields=['verification_status', 'verification_by', 'verified_at'])
    # Notify owner via email
    owner = deck.owner
    if getattr(owner, 'email_notifications', False) and getattr(owner, 'email', ''):
        try:
            send_mail(
                subject='Your deck has been rejected',
                message=f'Your deck "{deck.title}" was rejected by a professor. Reason: {reason if reason else "No reason provided."}',
                from_email=None,
                recipient_list=[owner.email],
                fail_silently=True,
            )
        except Exception:
            pass
    messages.success(request, f'"{deck.title}" rejected successfully.')
    return redirect('flashcards:deck_moderation_list')


@login_required
@require_http_methods(["POST"])
def bulk_verify_decks(request: HttpRequest) -> HttpResponse:
    """Bulk verify selected decks."""
    if not (getattr(request.user, 'is_professor', False) or request.user.is_staff):
        messages.error(request, 'Permission denied.')
        return redirect('flashcards:deck_list')
    ids = request.POST.getlist('deck_ids')
    if not ids:
        messages.warning(request, 'No decks selected.')
        return redirect('flashcards:deck_moderation_list')
    decks = Deck.objects.filter(pk__in=ids, visibility='public', verification_status='pending')
    verified_count = 0
    for deck in decks:
        deck.verification_status = 'verified'
        deck.verification_by = request.user
        deck.verified_at = timezone.now()
        deck.save(update_fields=['verification_status', 'verification_by', 'verified_at'])
        owner = deck.owner
        if getattr(owner, 'email_notifications', False) and getattr(owner, 'email', ''):
            try:
                send_mail(
                    subject='Your deck has been verified',
                    message=f'Your deck "{deck.title}" is now verified and visible in All Decks.',
                    from_email=None,
                    recipient_list=[owner.email],
                    fail_silently=True,
                )
            except Exception:
                pass
        verified_count += 1
    messages.success(request, f'Verified {verified_count} deck{"s" if verified_count != 1 else ""}.')
    return redirect('flashcards:deck_moderation_list')
