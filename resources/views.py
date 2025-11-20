from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import OperationalError
from django.utils import timezone
from django.db.models import Q
from .models import Resource, Tag, Bookmark, Rating, Comment
from .forms import ResourceUploadForm, RatingForm, CommentForm
from .supabase_storage import supabase_storage
from django.utils.timesince import timesince


# --- General Views ---

def home(request):
    """Temporary redirect to dashboard with feature-in-progress message"""
    messages.info(request, 'The Resources feature is currently under development. Please check back soon!')
    return redirect('accounts:dashboard')


# --- Resource Upload Views ---

@login_required
def resource_upload(request):
    """Upload a new resource"""
    if request.method == 'POST':
        form = ResourceUploadForm(request.POST, request.FILES)
        if form.is_valid():
            resource = form.save(commit=False)
            resource.uploader = request.user
            
            # Handle file upload to Supabase
            if 'file' in request.FILES:
                uploaded_file = request.FILES['file']
                
                # Upload to Supabase
                success, file_url, error = supabase_storage.upload_file(
                    uploaded_file, 
                    folder="resources"
                )
                
                if success:
                    resource.file_url = file_url
                    resource.original_filename = uploaded_file.name
                    resource.file_size = uploaded_file.size
                else:
                    messages.error(request, f'File upload failed: {error}')
                    return render(request, 'resources/resource_upload.html', {'form': form})
            
            # Approval / verification logic:
            # Professors: auto-verify regardless of visibility.
            # Non-professors:
            #   - If uploaded as private (is_public=False): treat as verified immediately (no approval needed).
            #   - If uploaded as public (is_public=True): mark as pending until professor approval.
            if getattr(request.user, 'is_professor', False):
                resource.verification_status = 'verified'
                resource.approved = True
                resource.verification_by = request.user
                resource.verified_at = timezone.now()
            else:
                if resource.is_public:
                    resource.verification_status = 'pending'
                    resource.approved = False
                    resource.verification_by = None
                    resource.verified_at = None
                else:  # private upload -> auto verified
                    resource.verification_status = 'verified'
                    resource.approved = True
                    resource.verification_by = request.user  # owner acts as implicit verifier
                    resource.verified_at = timezone.now()
            
            resource.save()
            form.save_m2m()  # Save tags
            
            # Different success messages based on role
            if getattr(request.user, 'is_professor', False):
                messages.success(request, 'Resource uploaded and published successfully!')
            else:
                messages.success(request, 'Resource uploaded successfully! It is pending verification.')
            
            return redirect('resources:resource_detail', pk=resource.pk)
    else:
        form = ResourceUploadForm()
    
    return render(request, 'resources/resource_upload.html', {'form': form})


@login_required
def resource_detail(request, pk):
    """View a specific resource with a concise layout (stats + actions)."""
    resource = get_object_or_404(Resource, pk=pk)

    # Restrict access to private resources to uploader only
    if not resource.is_public and resource.uploader != request.user:
        messages.error(request, 'This resource is private.')
        return redirect('resources:resource_list')

    # Restrict access to unverified resources to uploader or professors
    if resource.verification_status != 'verified':
        if not (resource.uploader == request.user or getattr(request.user, 'is_professor', False)):
            messages.error(request, 'This resource is pending verification.')
            return redirect('resources:resource_list')

    # Increment view count
    resource.increment_view_count()

    # Bookmark state for current user (shows toggle button)
    is_bookmarked = False
    if request.user.is_authenticated:
        is_bookmarked = Bookmark.objects.filter(user=request.user, resource=resource).exists()

    context = {
        'resource': resource,
        'is_bookmarked': is_bookmarked,
    }
    return render(request, 'resources/resource_detail.html', context)


@login_required
def my_resources(request):
    """List all resources uploaded by the current user"""
    resources = Resource.objects.filter(uploader=request.user).order_by('-created_at')
    bookmarked_ids = set()
    if request.user.is_authenticated:
        bookmarked_ids = set(
            Bookmark.objects.filter(user=request.user, resource__in=resources)
            .values_list('resource_id', flat=True)
        )
    context = {
        'resources': resources,
        'is_my_resources': True,
        'bookmarked_ids': bookmarked_ids,
    }
    return render(request, 'resources/resource_list.html', context)


@login_required
def resource_list(request):
    """List resources: 'All Resources' shows:
    - Professors: verified + pending public resources.
    - Regular users: verified public resources only.
    Private resources never shown here.
    """
    from django.core.paginator import Paginator
    
    if getattr(request.user, 'is_professor', False):
        resources = Resource.objects.filter(is_public=True).filter(
            Q(verification_status='verified') | Q(verification_status='pending')
        )
    else:
        resources = Resource.objects.filter(is_public=True, verification_status='verified')
    
    # Filter by resource type if provided
    resource_type = request.GET.get('resource_type')
    if resource_type:
        resources = resources.filter(resource_type=resource_type)
    
    # Filter by tags if provided
    tag_filter = request.GET.get('tag')
    if tag_filter:
        resources = resources.filter(tags__name=tag_filter)
    
    # Search functionality
    search_query = request.GET.get('q')
    if search_query:
        resources = resources.filter(
            Q(title__icontains=search_query) | Q(description__icontains=search_query)
        )
    
    # Order by created_at
    resources = resources.order_by('-created_at')
    
    # Pagination
    paginator = Paginator(resources, 12)  # 12 items per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    tags_list = Tag.objects.all().order_by('name')
    
    # Resource type filter options for component
    resource_type_options = [
        {'value': 'pdf', 'label': 'PDF'},
        {'value': 'ppt', 'label': 'PPT'},
        {'value': 'pptx', 'label': 'PPTX'},
        {'value': 'docx', 'label': 'DOCX'},
        {'value': 'image', 'label': 'Image'},
        {'value': 'link', 'label': 'Link'},
        {'value': 'txt', 'label': 'Text'},
    ]
    
    context = {
        'resources': page_obj,
        'search_query': search_query,
        'tag_filter': tag_filter,
        'bookmarked_ids': set(
            Bookmark.objects.filter(user=request.user, resource__in=page_obj.object_list)
            .values_list('resource_id', flat=True)
        ) if request.user.is_authenticated else set(),
        'tags_list': tags_list,
        'resource_type_options': resource_type_options,
    }
    return render(request, 'resources/resource_list.html', context)

@login_required
def resource_list_api(request):
    """JSON API: filtered/paginated resources for reactive front-end.
    Scope rules:
            - all: verified public resources (plus pending public for professors)
      - mine: all resources uploaded by the user (public or private, any verification status)
    """
    from django.core.paginator import Paginator

    scope = request.GET.get('scope', 'all')
    if scope == 'mine':
        # Show only user's uploads (any verification status, any visibility)
        resources_qs = Resource.objects.filter(uploader=request.user)
    else:
        # All scope with professor pending access
        if getattr(request.user, 'is_professor', False):
            resources_qs = Resource.objects.filter(is_public=True).filter(
                Q(verification_status='verified') | Q(verification_status='pending')
            )
        else:
            resources_qs = Resource.objects.filter(is_public=True, verification_status='verified')

    resource_type = request.GET.get('resource_type')
    if resource_type:
        resources_qs = resources_qs.filter(resource_type=resource_type)

    tag_filter = request.GET.get('tag')
    if tag_filter:
        resources_qs = resources_qs.filter(tags__name__iexact=tag_filter)

    search_query = request.GET.get('q')
    if search_query:
        resources_qs = resources_qs.filter(
            Q(title__icontains=search_query) | Q(description__icontains=search_query)
        )

    resources_qs = resources_qs.order_by('-created_at').distinct()

    page_size = int(request.GET.get('page_size', 12))
    page_number = request.GET.get('page', 1)
    paginator = Paginator(resources_qs, page_size)
    page_obj = paginator.get_page(page_number)

    data = []
    for r in page_obj.object_list.select_related('uploader').prefetch_related('tags'):
        data.append({
            'id': r.id,
            'title': r.title,
            'resource_type': r.resource_type,
            'verification_status': r.verification_status,
            'is_public': r.is_public,
            'views_count': r.views_count,
            'download_count': r.download_count,
            'average_rating': r.get_average_rating(),
            'rating_count': r.get_rating_count(),
            'tags': [t.name for t in r.tags.all()[:6]],
            'tags_extra': max(r.tags.count() - 6, 0),
            'uploader': getattr(r.uploader, 'get_full_name', lambda: r.uploader.username)() or r.uploader.username,
            'created_at': r.created_at.isoformat(),
            'created_since': timesince(r.created_at) + ' ago',
            'bookmarked': request.user.is_authenticated and Bookmark.objects.filter(user=request.user, resource=r).exists(),
        })

    return JsonResponse({
        'success': True,
        'results': data,
        'page': page_obj.number,
        'num_pages': paginator.num_pages,
        'has_next': page_obj.has_next(),
        'has_previous': page_obj.has_previous(),
        'total': paginator.count,
    })

# bookmark_toggle view removed (feature deprecated)


@login_required
def moderation_list(request):
    """List pending resources, quizzes, and flashcards for professors to review"""
    if not getattr(request.user, 'is_professor', False):
        messages.error(request, 'You do not have permission to access moderation.')
        return redirect('resources:resource_list')
    
    # Get all pending items for moderation
    from quizzes.models import Quiz
    from flashcards.models import Deck
    pending_resources = Resource.objects.filter(verification_status='pending').order_by('-created_at')
    pending_quizzes = Quiz.objects.filter(verification_status='pending').order_by('-created_at')
    pending_decks = Deck.objects.filter(verification_status='pending', visibility='public').order_by('-created_at')
    
    context = {
        'pending_resources': pending_resources,
        'pending_quizzes': pending_quizzes,
        'pending_decks': pending_decks,
    }
    return render(request, 'resources/moderation_list.html', context)


@login_required
def verified_resources_list(request):
    """List recently verified resources for professors"""
    if not getattr(request.user, 'is_professor', False):
        messages.error(request, 'You do not have permission to access this page.')
        return redirect('resources:resource_list')
    verified = Resource.objects.filter(
        verification_status='verified',
        verification_by=request.user
    ).order_by('-verified_at')
    return render(request, 'resources/verified_resources_list.html', { 'verified_resources': verified })


@login_required
def approve_resource(request, pk):
    """Approve and verify a resource (professors only)"""
    if not getattr(request.user, 'is_professor', False):
        messages.error(request, 'You do not have permission to perform this action.')
        return redirect('resources:resource_list')
    resource = get_object_or_404(Resource, pk=pk)
    if request.method == 'POST':
        resource.verification_status = 'verified'
        resource.approved = True
        resource.verification_by = request.user
        resource.verified_at = timezone.now()
        resource.save(update_fields=['verification_status', 'approved', 'verification_by', 'verified_at'])
        messages.success(request, f'"{resource.title}" approved and published.')
    
    # Redirect to the referring page or moderation list
    next_url = request.GET.get('next', 'resources:moderation_list')
    if next_url.startswith('/'):
        return redirect(next_url)
    return redirect('resources:moderation_list')


@login_required
def reject_resource(request, pk):
    """Reject a resource (professors only)"""
    if not getattr(request.user, 'is_professor', False):
        messages.error(request, 'You do not have permission to perform this action.')
        return redirect('resources:resource_list')
    resource = get_object_or_404(Resource, pk=pk)
    if request.method == 'POST':
        resource.verification_status = 'not_verified'
        resource.approved = False
        resource.verification_by = request.user
        resource.verified_at = timezone.now()
        resource.save(update_fields=['verification_status', 'approved', 'verification_by', 'verified_at'])
        messages.info(request, f'"{resource.title}" has been rejected.')
    
    # Redirect to the referring page or moderation list
    next_url = request.GET.get('next', 'resources:moderation_list')
    if next_url.startswith('/'):
        return redirect(next_url)
    return redirect('resources:moderation_list')


@login_required
def resource_edit(request, pk):
    """Edit an existing resource"""
    resource = get_object_or_404(Resource, pk=pk)
    
    # Restrict access to private resources to uploader only
    if not resource.is_public and resource.uploader != request.user:
        messages.error(request, 'This resource is private.')
        return redirect('resources:resource_list')
    
    # Only uploader can edit
    if resource.uploader != request.user:
        messages.error(request, 'You can only edit your own resources.')
        return redirect('resources:resource_detail', pk=pk)
    
    if request.method == 'POST':
        form = ResourceUploadForm(request.POST, request.FILES, instance=resource)
        if form.is_valid():
            # Save core fields but handle tags manually to support comma input UI
            resource_obj = form.save(commit=False)

            # Track original visibility to detect changes
            original_public = resource.is_public
            new_public = resource_obj.is_public

            # Handle new file upload if provided
            if 'file' in request.FILES:
                uploaded_file = request.FILES['file']
                
                # Delete old file if exists
                if resource.file_url:
                    supabase_storage.delete_file(resource.file_url)
                
                # Upload new file
                success, file_url, error = supabase_storage.upload_file(
                    uploaded_file,
                    folder="resources"
                )
                
                if success:
                    resource_obj.file_url = file_url
                    resource_obj.original_filename = uploaded_file.name
                    resource_obj.file_size = uploaded_file.size
                else:
                    messages.error(request, f'File upload failed: {error}')
                    return render(request, 'resources/resource_edit.html', {
                        'form': form,
                        'resource': resource
                    })

            # Visibility transition logic for non-professor uploader:
            # - private -> public: set to pending (requires approval)
            # - public -> private: auto-verify if not already verified
            if not getattr(request.user, 'is_professor', False) and resource.uploader == request.user:
                if (not original_public) and new_public:
                    resource_obj.verification_status = 'pending'
                    resource_obj.approved = False
                    resource_obj.verification_by = None
                    resource_obj.verified_at = None
                elif original_public and (not new_public):
                    # Moving to private; verification no longer depends on professor approval
                    if resource_obj.verification_status != 'verified':
                        resource_obj.verification_status = 'verified'
                        resource_obj.approved = True
                        resource_obj.verification_by = request.user
                        resource_obj.verified_at = timezone.now()

            # Persist main changes
            resource_obj.save()

            # Tags: prefer comma-separated input if provided
            tags_text = request.POST.get('tags_text', None)
            if tags_text is not None:
                tag_names = [t.strip() for t in tags_text.split(',') if t.strip()]
                tag_objs = []
                for name in tag_names:
                    tag, _ = Tag.objects.get_or_create(name=name)
                    tag_objs.append(tag)
                resource_obj.tags.set(tag_objs)
            else:
                # Fall back to form's m2m if our custom field wasn't used
                form.save_m2m()

            # Refresh instance for template usage/redirect
            resource = resource_obj
            messages.success(request, 'Resource updated successfully!')
            return redirect('resources:resource_detail', pk=pk)
    else:
        form = ResourceUploadForm(instance=resource)
    
    context = {
        'form': form,
        'resource': resource,
    }
    return render(request, 'resources/resource_edit.html', context)


@login_required
def resource_delete(request, pk):
    """Delete a resource"""
    resource = get_object_or_404(Resource, pk=pk)
    
    # Restrict access to private resources to uploader only
    if not resource.is_public and resource.uploader != request.user:
        messages.error(request, 'This resource is private.')
        return redirect('resources:resource_list')
    
    # Only uploader or admin can delete
    if resource.uploader != request.user and not request.user.is_staff:
        messages.error(request, 'You can only delete your own resources.')
        return redirect('resources:resource_detail', pk=pk)
    
    if request.method == 'POST':
        # Delete file from Supabase if exists
        if resource.file_url:
            supabase_storage.delete_file(resource.file_url)
        
        resource.delete()
        messages.success(request, 'Resource deleted successfully.')
        return redirect('resources:resource_list')
    
    return render(request, 'resources/resource_delete.html', {'resource': resource})


@login_required
def resource_download(request, pk):
    """Track download and redirect to file"""
    resource = get_object_or_404(Resource, pk=pk)
    
    # Restrict access to private resources to uploader only
    if not resource.is_public and resource.uploader != request.user:
        messages.error(request, 'This resource is private.')
        return redirect('resources:resource_list')
    
    # Increment download count
    resource.increment_download_count()
    
    # Redirect to file URL
    if resource.file_url:
        return redirect(resource.file_url)
    elif resource.external_url:
        return redirect(resource.external_url)
    else:
        messages.error(request, 'No file available for download.')
        return redirect('resources:resource_detail', pk=pk)


@login_required
def rate_resource(request, pk):
    """Rate a resource"""
    resource = get_object_or_404(Resource, pk=pk)
    
    # Restrict access to private resources to uploader only
    if not resource.is_public and resource.uploader != request.user:
        messages.error(request, 'This resource is private.')
        return redirect('resources:resource_list')
    # Prevent owner from rating own resource
    if resource.uploader == request.user:
        messages.error(request, 'You cannot rate your own resource.')
        return redirect('resources:resource_detail', pk=pk)
    
    if request.method == 'POST':
        stars = request.POST.get('stars')
        
        # Validate that stars value is provided
        if not stars:
            messages.error(request, 'Please select a star rating before submitting.')
            return redirect('resources:resource_detail', pk=pk)
        
        try:
            stars = int(stars)
            if stars < 1 or stars > 5:
                messages.error(request, 'Rating must be between 1 and 5 stars.')
                return redirect('resources:resource_detail', pk=pk)
        except (ValueError, TypeError):
            messages.error(request, 'Invalid rating value.')
            return redirect('resources:resource_detail', pk=pk)
        
        # Get or create rating
        rating, created = Rating.objects.get_or_create(
            user=request.user,
            resource=resource,
            defaults={'stars': stars}
        )

        # Update if already exists
        if not created:
            rating.stars = stars
            rating.save()

        action = 'rated' if created else 'updated rating for'
        avg_rating = resource.get_average_rating()
        rating_count = resource.get_rating_count()

        # AJAX response
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True,
                'message': f'You {action} "{resource.title}" with {stars} star{"s" if stars != 1 else ""}! ',
                'avg_rating': avg_rating,
                'rating_count': rating_count,
                'user_stars': rating.stars,
            })

        messages.success(request, f'You {action} "{resource.title}" with {stars} star{"s" if stars != 1 else ""}!')
    return redirect('resources:resource_detail', pk=pk)


@login_required
def add_comment(request, pk):
    """Add a comment to a resource"""
    resource = get_object_or_404(Resource, pk=pk)
    
    # Restrict access to private resources to uploader only
    if not resource.is_public and resource.uploader != request.user:
        messages.error(request, 'This resource is private.')
        return redirect('resources:resource_list')
    # Prevent owner from commenting on own resource
    if resource.uploader == request.user:
        messages.error(request, 'You cannot comment on your own resource.')
        return redirect('resources:resource_detail', pk=pk)
    
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.user = request.user
            comment.resource = resource
            comment.save()
            messages.success(request, 'Comment added successfully!')
        else:
            messages.error(request, 'Error adding comment.')
    
    return redirect('resources:resource_detail', pk=pk)


@login_required
def delete_comment(request, pk):
    """Delete a comment"""
    comment = get_object_or_404(Comment, pk=pk)
    resource_pk = comment.resource.pk
    
    # Only the comment author can delete
    if comment.user == request.user:
        comment.delete()
        messages.success(request, 'Comment deleted successfully.')
    else:
        messages.error(request, 'You can only delete your own comments.')
    
    return redirect('resources:resource_detail', pk=resource_pk)

