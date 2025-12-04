from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.urls import reverse
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
    from .models import DeckBookmark
    
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

    # Get user's bookmarked decks for this view
    bookmarked_deck_ids = set()
    if request.user.is_authenticated:
        bookmarked_deck_ids = set(
            DeckBookmark.objects.filter(user=request.user, deck__in=decks).values_list('deck_id', flat=True)
        )

    # Add like status and bookmark status for each deck
    for deck in decks:
        if request.user.is_authenticated:
            deck.user_has_liked = deck.likes.filter(user=request.user).exists()
            deck.user_bookmarked = deck.pk in bookmarked_deck_ids
        else:
            deck.user_has_liked = False
            deck.user_bookmarked = False

    # Category filter options for component
    category_options = [
        {'value': 'general', 'label': 'General'},
        {'value': 'definitions', 'label': 'Definitions'},
        {'value': 'formulas', 'label': 'Formulas'},
        {'value': 'concepts', 'label': 'Concepts'},
        {'value': 'language', 'label': 'Language'},
    ]

    return render(
        request,
        "flashcards/deck_list.html",
        {
            "decks": decks,
            "query": q,
            "selected_category": category,
            "scope": scope,
            "category_options": category_options,
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
    from .models import DeckBookmark
    
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

    # Check if user has bookmarked this deck
    is_bookmarked = False
    user_has_liked = False
    if request.user.is_authenticated:
        is_bookmarked = DeckBookmark.objects.filter(user=request.user, deck=deck).exists()
        from .models import DeckLike
        user_has_liked = DeckLike.objects.filter(user=request.user, deck=deck).exists()

    # Get URLs for template
    from django.urls import reverse
    comment_url = reverse('flashcards:add_deck_comment', args=[deck.pk])
    rate_url = reverse('flashcards:rate_deck', args=[deck.pk])

    return render(
        request,
        "flashcards/deck_detail.html",
        {
            "deck": deck,
            "cards": cards,
            "card_form": card_form,
            "user_rating": user_rating,
            "comments": comments,
            "is_bookmarked": is_bookmarked,
            "user_has_liked": user_has_liked,
            "comment_url": comment_url,
            "rate_url": rate_url,
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
    deck = get_object_or_404(Deck, pk=pk)
    # Allow owner, professor, or admin to delete
    if deck.owner != request.user and not getattr(request.user, 'is_professor', False) and not request.user.is_staff:
        from django.http import HttpResponseForbidden
        return HttpResponseForbidden("You can only delete your own decks.")
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
    from .models import DeckBookmark
    
    deck = get_object_or_404(Deck, pk=pk)
    # No ownership check needed - anyone can bookmark any public/their own deck
    bookmark, created = DeckBookmark.objects.get_or_create(user=request.user, deck=deck)
    if not created:
        bookmark.delete()
        is_bookmarked = False
    else:
        is_bookmarked = True
    
    if request.headers.get("x-requested-with") == "XMLHttpRequest":
        return JsonResponse({"bookmarked": is_bookmarked})
    
    # Redirect back to referring page or deck detail
    next_url = request.POST.get('next') or request.META.get('HTTP_REFERER')
    if next_url and next_url.startswith("/"):
        return redirect(next_url)
    return redirect("flashcards:deck_detail", pk=pk)


@login_required
def toggle_like(request: HttpRequest, pk: int) -> HttpResponse:
    """Toggle like status for deck. Supports AJAX JSON or redirect fallback."""
    from .models import DeckLike
    
    deck = get_object_or_404(Deck, pk=pk)
    # No ownership check needed - anyone can like any public/their own deck
    like, created = DeckLike.objects.get_or_create(user=request.user, deck=deck)
    if not created:
        like.delete()
        is_liked = False
    else:
        is_liked = True
    
    # Get updated like count
    like_count = deck.likes.count()
    
    if request.headers.get("x-requested-with") == "XMLHttpRequest":
        return JsonResponse({"liked": is_liked, "like_count": like_count})
    
    # Redirect back to referring page or deck detail
    next_url = request.POST.get('next') or request.META.get('HTTP_REFERER')
    if next_url and next_url.startswith("/"):
        return redirect(next_url)
    return redirect("flashcards:deck_detail", pk=pk)


@login_required
def rate_deck(request: HttpRequest, pk: int) -> HttpResponse:
    """Rate a deck (supports AJAX)"""
    deck = get_object_or_404(Deck, pk=pk)
    
    # Check if AJAX request
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
    
    if deck.owner == request.user:
        if is_ajax:
            return JsonResponse({'success': False, 'message': 'You cannot rate your own deck.'}, status=403)
        from django.contrib import messages
        messages.error(request, 'You cannot rate your own deck.')
        return redirect('flashcards:deck_detail', pk=pk)
    
    if deck.visibility != 'public' or deck.verification_status != 'verified':
        if is_ajax:
            return JsonResponse({'success': False, 'message': 'You can only rate public decks.'}, status=403)
        from django.contrib import messages
        messages.error(request, 'You can only rate public decks.')
        return redirect('flashcards:deck_detail', pk=pk)
    
    if request.method == 'POST':
        stars = request.POST.get('stars')
        if not stars:
            if is_ajax:
                return JsonResponse({'success': False, 'message': 'Please select a rating.'}, status=400)
            from django.contrib import messages
            messages.error(request, 'Please select a rating.')
            return redirect('flashcards:deck_detail', pk=pk)
        
        try:
            stars_int = int(stars)
            if stars_int < 1 or stars_int > 5:
                raise ValueError()
        except ValueError:
            if is_ajax:
                return JsonResponse({'success': False, 'message': 'Invalid rating value.'}, status=400)
            from django.contrib import messages
            messages.error(request, 'Invalid rating value.')
            return redirect('flashcards:deck_detail', pk=pk)
        
        rating, created = DeckRating.objects.get_or_create(user=request.user, deck=deck, defaults={'stars': stars_int})
        if not created:
            rating.stars = stars_int
            rating.save()
        
        action = 'rated' if created else 'updated your rating for'
        message = f'You {action} "{deck.title}" with {stars_int} star' + ('s' if stars_int != 1 else '') + '!'
        
        if is_ajax:
            return JsonResponse({
                'success': True,
                'message': message,
                'new_average': deck.get_average_rating(),
                'rating_count': deck.get_rating_count()
            })
        
        from django.contrib import messages
        messages.success(request, message)
    
    return redirect('flashcards:deck_detail', pk=pk)


@login_required
def add_deck_comment(request: HttpRequest, pk: int) -> HttpResponse:
    """Add a comment to a deck (supports AJAX)"""
    deck = get_object_or_404(Deck, pk=pk)
    
    # Check if AJAX request
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
    
    # Restrict access to private decks to owner only
    if deck.visibility != 'public' and deck.owner != request.user:
        if is_ajax:
            return JsonResponse({'success': False, 'error': 'This deck is private.'}, status=403)
        from django.contrib import messages
        messages.error(request, 'This deck is private.')
        return redirect('flashcards:flashcard_hub')
    
    if request.method == 'POST':
        # Check if this is a reply or a top-level comment
        parent_id = request.POST.get('parent_comment_id')
        
        # Prevent owner from adding TOP-LEVEL comments only (replies are allowed)
        if deck.owner == request.user and not parent_id:
            if is_ajax:
                return JsonResponse({'success': False, 'error': 'You cannot add top-level comments on your own deck.'}, status=403)
            from django.contrib import messages
            messages.error(request, 'You cannot add top-level comments on your own deck.')
            return redirect('flashcards:deck_detail', pk=pk)
        
        form = DeckCommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.user = request.user
            comment.deck = deck
            
            # Handle parent comment for threading
            parent_id = request.POST.get('parent_comment_id')
            if parent_id:
                try:
                    parent_comment = DeckComment.objects.get(pk=parent_id, deck=deck)
                    comment.parent_comment = parent_comment
                except DeckComment.DoesNotExist:
                    pass
            
            comment.save()
            
            # AJAX response with comment data
            if is_ajax:
                from django.utils.timesince import timesince
                return JsonResponse({
                    'success': True,
                    'message': 'Comment added successfully!',
                    'comment': {
                        'id': comment.id,
                        'text': comment.text,
                        'user_name': comment.user.get_display_name(),
                        'user_initial': comment.user.get_display_name()[0].upper() if comment.user.get_display_name() else 'U',
                        'is_professor': getattr(comment.user, 'is_professor', False),
                        'created_at': comment.created_at.strftime('%b %d, %Y at %I:%M %p'),
                        'created_since': timesince(comment.created_at) + ' ago',
                        'can_delete': comment.user == request.user,
                        'delete_url': f'/flashcards/{deck.pk}/comment/{comment.id}/delete/',
                    }
                })
            
            from django.contrib import messages
            messages.success(request, 'Comment added successfully!')
        else:
            if is_ajax:
                return JsonResponse({'success': False, 'error': 'Invalid comment data. Please check your input.'}, status=400)
            from django.contrib import messages
            messages.error(request, 'Error adding comment.')
    
    return redirect('flashcards:deck_detail', pk=pk)


@login_required
def edit_deck_comment(request: HttpRequest, pk: int) -> HttpResponse:
    """Edit a comment (AJAX only)"""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'POST required'}, status=405)
    
    comment = get_object_or_404(DeckComment, pk=pk)
    
    # Only the comment author can edit
    if comment.user != request.user:
        return JsonResponse({'success': False, 'error': 'You can only edit your own comments.'}, status=403)
    
    text = request.POST.get('text', '').strip()
    if not text:
        return JsonResponse({'success': False, 'error': 'Comment cannot be empty.'}, status=400)
    
    comment.text = text
    comment.save()
    
    return JsonResponse({'success': True, 'message': 'Comment updated successfully.'})


@login_required
def delete_deck_comment(request: HttpRequest, pk: int) -> HttpResponse:
    """Delete a comment"""
    comment = get_object_or_404(DeckComment, pk=pk)
    deck_pk = comment.deck.pk
    
    # Only the comment author can delete
    if comment.user == request.user:
        comment.delete()
        from django.contrib import messages
        messages.success(request, 'Comment deleted successfully.')
    else:
        from django.contrib import messages
        messages.error(request, 'You can only delete your own comments.')
    
    return redirect('flashcards:deck_detail', pk=deck_pk)


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


@login_required
@require_http_methods(["POST"])
def update_deck_title(request: HttpRequest, pk: int) -> JsonResponse:
    """AJAX endpoint to update deck title."""
    deck = get_object_or_404(Deck, pk=pk, owner=request.user)
    try:
        data = json.loads(request.body)
        new_title = data.get('title', '').strip()
        if not new_title:
            return JsonResponse({'success': False, 'error': 'Title cannot be empty.'}, status=400)
        
        deck.title = new_title
        deck.save(update_fields=['title'])
        return JsonResponse({'success': True, 'title': deck.title})
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'error': 'Invalid JSON.'}, status=400)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@login_required
@require_http_methods(["POST"])
def update_card(request: HttpRequest, pk: int, card_id: int) -> JsonResponse:
    """AJAX endpoint to update card content."""
    deck = get_object_or_404(Deck, pk=pk, owner=request.user)
    card = get_object_or_404(Card, pk=card_id, deck=deck)
    try:
        data = json.loads(request.body)
        front_text = data.get('front_text', '').strip()
        back_text = data.get('back_text', '').strip()
        
        if not front_text or not back_text:
            return JsonResponse({'success': False, 'error': 'Front and back text cannot be empty.'}, status=400)
        
        card.front_text = front_text
        card.back_text = back_text
        card.save(update_fields=['front_text', 'back_text'])
        return JsonResponse({
            'success': True, 
            'front_text': card.front_text,
            'back_text': card.back_text
        })
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'error': 'Invalid JSON.'}, status=400)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)
