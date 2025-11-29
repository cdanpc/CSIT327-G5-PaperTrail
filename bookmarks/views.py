from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib import messages

from resources.models import Resource, Bookmark
from flashcards.models import Deck, DeckBookmark
from quizzes.models import QuizBookmark
from django.db.models import Q
from django.http import JsonResponse
from django.utils.timesince import timesince


@login_required
def bookmark_list(request):
    """List user's bookmarks with optional search, tag filter, and pagination."""
    # Top-level bookmark type filter: resources | quizzes | flashcards | ''(all)
    btype = request.GET.get("btype", "").strip()
    q = request.GET.get("q", "").strip()

    # Collect resources bookmarks
    res_qs = (
        Bookmark.objects.filter(user=request.user)
        .select_related("resource", "resource__uploader")
        .prefetch_related("resource__tags")
    )
    if q:
        res_qs = res_qs.filter(
            Q(resource__title__icontains=q) | Q(resource__description__icontains=q)
        )
    # Collect quizzes bookmarks
    quiz_qs = QuizBookmark.objects.filter(user=request.user).select_related('quiz', 'quiz__creator')
    if q:
        quiz_qs = quiz_qs.filter(Q(quiz__title__icontains=q) | Q(quiz__description__icontains=q))
    # Collect flashcards bookmarks (using DeckBookmark model for per-user tracking)
    deck_bm_qs = DeckBookmark.objects.filter(user=request.user).select_related('deck', 'deck__owner')
    if q:
        deck_bm_qs = deck_bm_qs.filter(Q(deck__title__icontains=q) | Q(deck__description__icontains=q))

    # Build unified items
    items = []
    if btype in ("", "resources"):
        for b in res_qs:
            r = b.resource
            user_has_liked = r.likes.filter(user=request.user).exists() if request.user.is_authenticated else False
            items.append({
                'type': 'resource',
                'id': r.id,
                'title': r.title,
                'is_private': not r.is_public,
                'verification_status': r.verification_status,
                'resource_type': r.resource_type,
                'views': r.views_count,
                'downloads': r.download_count,
                'rating': r.get_average_rating(),
                'likes_count': r.likes.count(),
                'user_has_liked': user_has_liked,
                'author': getattr(r.uploader, 'get_full_name', lambda: r.uploader.username)() or r.uploader.username,
                'detail_url': reverse('resources:resource_detail', args=[r.id]),
                'remove_url': reverse('bookmarks:toggle', args=[r.id]),
                'created_at': b.created_at,
            })
    if btype in ("", "quizzes"):
        for qb in quiz_qs:
            qz = qb.quiz
            # get_display_name may be method; fallback to username
            author = getattr(qz.creator, 'get_display_name', None)
            author_str = author() if callable(author) else (getattr(qz.creator, 'get_full_name', lambda: qz.creator.username)() or qz.creator.username)
            user_has_liked = qz.likes.filter(user=request.user).exists() if request.user.is_authenticated else False
            items.append({
                'type': 'quiz',
                'id': qz.id,
                'title': qz.title,
                'is_private': not qz.is_public,
                'verification_status': qz.verification_status,
                'questions': qz.total_questions,
                'attempts': qz.attempts_count,
                'likes_count': qz.likes.count(),
                'user_has_liked': user_has_liked,
                'author': author_str,
                'detail_url': reverse('quizzes:quiz_detail', args=[qz.id]),
                'remove_url': reverse('quizzes:toggle_quiz_bookmark', args=[qz.id]),
                'created_at': qb.created_at,
            })
    if btype in ("", "flashcards"):
        for deck_bm in deck_bm_qs:
            d = deck_bm.deck
            owner = d.owner
            author_str = getattr(owner, 'get_full_name', lambda: owner.username)() or owner.username
            user_has_liked = d.likes.filter(user=request.user).exists() if request.user.is_authenticated else False
            items.append({
                'type': 'flashcard',
                'id': d.id,
                'title': d.title,
                'is_private': d.visibility == 'private',
                'verification_status': d.verification_status,
                'cards': d.cards_count,
                'likes_count': d.likes.count(),
                'user_has_liked': user_has_liked,
                'author': author_str,
                'detail_url': reverse('flashcards:deck_detail', args=[d.id]),
                'remove_url': reverse('flashcards:bookmark_toggle', args=[d.id]),
                'created_at': deck_bm.created_at,
            })

    # Sort by most recent bookmark/time
    items.sort(key=lambda x: x['created_at'], reverse=True)

    # Filter options for component
    filter_options = [
        {'value': '', 'label': 'All'},
        {'value': 'resources', 'label': 'Resources'},
        {'value': 'quizzes', 'label': 'Quizzes'},
        {'value': 'flashcards', 'label': 'Flashcards'},
    ]

    return render(
        request,
        "bookmarks/bookmark_list.html",
        {
            "btype": btype,
            "items": items,
            "filter_options": filter_options,
        },
    )


@login_required
def toggle_bookmark(request, resource_id):
    if request.method != "POST":
        return redirect("bookmarks:bookmark_list")

    resource = get_object_or_404(Resource, pk=resource_id)

    bookmark, created = Bookmark.objects.get_or_create(user=request.user, resource=resource)
    if not created:
        bookmark.delete()
        messages.info(request, f'Removed bookmark for "{resource.title}"')
    else:
        messages.success(request, f'Bookmarked "{resource.title}"')

    next_url = request.POST.get("next") or request.META.get("HTTP_REFERER")
    if next_url and next_url.startswith("/"):
        return redirect(next_url)
    return redirect("bookmarks:bookmark_list")


@login_required
def bookmark_list_api(request):
    """Reactive JSON listing for user's bookmarked resources."""
    qs = (
        Bookmark.objects.filter(user=request.user)
        .select_related("resource", "resource__uploader")
        .prefetch_related("resource__tags")
    )

    # Filters
    resource_type = request.GET.get('resource_type')
    search = request.GET.get('q')

    if resource_type:
        qs = qs.filter(resource__resource_type=resource_type)
    if search:
        qs = qs.filter(
            Q(resource__title__icontains=search) |
            Q(resource__description__icontains=search) |
            Q(resource__tags__name__icontains=search)
        ).distinct()

    qs = qs.order_by('-id')  # Most recently bookmarked first

    # Pagination
    from django.core.paginator import Paginator
    page_size = int(request.GET.get('page_size', 12))
    page_number = request.GET.get('page', 1)
    paginator = Paginator(qs, page_size)
    page_obj = paginator.get_page(page_number)

    results = []
    for b in page_obj.object_list:
        r = b.resource
        results.append({
            'id': r.id,
            'title': r.title,
            'resource_type': r.resource_type,
            'verification_status': r.verification_status,
            'views_count': r.views_count,
            'download_count': r.download_count,
            'average_rating': r.get_average_rating(),
            'tags': [t.name for t in r.tags.all()[:4]],
            'tags_extra': max(r.tags.count() - 4, 0),
            'uploader': getattr(r.uploader, 'get_full_name', lambda: r.uploader.username)() or r.uploader.username,
            'created_since': timesince(r.created_at) + ' ago',
        })

    return JsonResponse({
        'success': True,
        'results': results,
        'page': page_obj.number,
        'num_pages': paginator.num_pages,
        'has_next': page_obj.has_next(),
        'has_previous': page_obj.has_previous(),
        'total': paginator.count,
    })
