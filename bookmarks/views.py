from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib import messages

from resources.models import Resource, Bookmark, Tag
from django.core.paginator import Paginator
from django.db.models import Q


@login_required
def bookmark_list(request):
    """List user's bookmarks with optional search, tag filter, and pagination."""
    qs = (
        Bookmark.objects.filter(user=request.user)
        .select_related("resource", "resource__uploader")
        .prefetch_related("resource__tags")
    )

    search = request.GET.get("q", "").strip()
    tag_name = request.GET.get("tag", "").strip()

    if search:
        qs = qs.filter(
            Q(resource__title__icontains=search)
            | Q(resource__description__icontains=search)
            | Q(resource__tags__name__icontains=search)
        ).distinct()
    if tag_name:
        qs = qs.filter(resource__tags__name=tag_name).distinct()

    paginator = Paginator(qs, 12)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    tags = Tag.objects.all().order_by("name")[:50]

    return render(
        request,
        "bookmarks/bookmark_list.html",
        {
            "bookmarks": page_obj,
            "search": search,
            "tag_name": tag_name,
            "tags": tags,
            "page_obj": page_obj,
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
