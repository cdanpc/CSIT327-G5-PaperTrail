from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib import messages

from resources.models import Resource, Bookmark


@login_required
def bookmark_list(request):
    bookmarks = (
        Bookmark.objects.filter(user=request.user)
        .select_related("resource", "resource__uploader")
        .prefetch_related("resource__tags")
    )
    return render(request, "bookmarks/bookmark_list.html", {"bookmarks": bookmarks})


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
