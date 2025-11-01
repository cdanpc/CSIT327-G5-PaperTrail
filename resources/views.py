from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import OperationalError
from django.utils import timezone
from django.db.models import Q
from .models import Resource, Tag, Bookmark, Rating, Comment
from .forms import ResourceUploadForm, RatingForm, CommentForm
from .supabase_storage import supabase_storage


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
            
            # Auto-approve resources from professors
            if getattr(request.user, 'is_professor', False):
                resource.verification_status = 'verified'
                resource.approved = True
                resource.verification_by = request.user
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
    """View a specific resource"""
    resource = get_object_or_404(Resource, pk=pk)
    
    # Restrict access to unverified resources to uploader or professors
    if resource.verification_status != 'verified':
        if not (resource.uploader == request.user or getattr(request.user, 'is_professor', False)):
            messages.error(request, 'This resource is pending verification.')
            return redirect('resources:resource_list')
    
    # Increment view count
    resource.increment_view_count()
    
    # Check if user has bookmarked this resource
    is_bookmarked = False
    if request.user.is_authenticated:
        is_bookmarked = Bookmark.objects.filter(
            user=request.user, 
            resource=resource
        ).exists()
    
    # Get user's rating if exists
    user_rating = None
    if request.user.is_authenticated:
        try:
            user_rating = Rating.objects.get(user=request.user, resource=resource)
        except Rating.DoesNotExist:
            pass
    
    # Get all comments
    comments = resource.comments.all().select_related('user')
    
    # Initialize forms
    rating_form = RatingForm(instance=user_rating)
    comment_form = CommentForm()
    
    context = {
        'resource': resource,
        'is_bookmarked': is_bookmarked,
        'user_rating': user_rating,
        'rating_form': rating_form,
        'comment_form': comment_form,
        'comments': comments,
    }
    return render(request, 'resources/resource_detail.html', context)


@login_required
def my_resources(request):
    """List all resources uploaded by the current user"""
    resources = Resource.objects.filter(uploader=request.user).order_by('-created_at')
    context = {
        'resources': resources,
        'is_my_resources': True,
    }
    return render(request, 'resources/resource_list.html', context)


@login_required
def resource_list(request):
    """List resources: show verified to everyone, plus the uploader's own."""
    from django.core.paginator import Paginator
    
    resources = Resource.objects.filter(Q(verification_status='verified') | Q(uploader=request.user))
    
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
    
    context = {
        'resources': page_obj,
        'search_query': search_query,
        'tag_filter': tag_filter,
    }
    return render(request, 'resources/resource_list.html', context)


@login_required
def moderation_list(request):
    """List pending resources for professors to review"""
    if not getattr(request.user, 'is_professor', False):
        messages.error(request, 'You do not have permission to access moderation.')
        return redirect('resources:resource_list')
    pending = Resource.objects.filter(verification_status='pending').order_by('-created_at')
    return render(request, 'resources/moderation_list.html', { 'pending_resources': pending })


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
    
    # Only uploader can edit
    if resource.uploader != request.user:
        messages.error(request, 'You can only edit your own resources.')
        return redirect('resources:resource_detail', pk=pk)
    
    if request.method == 'POST':
        form = ResourceUploadForm(request.POST, request.FILES, instance=resource)
        if form.is_valid():
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
                    resource.file_url = file_url
                    resource.original_filename = uploaded_file.name
                    resource.file_size = uploaded_file.size
                else:
                    messages.error(request, f'File upload failed: {error}')
                    return render(request, 'resources/resource_edit.html', {
                        'form': form,
                        'resource': resource
                    })
            
            form.save()
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
        messages.success(request, f'You {action} "{resource.title}" with {stars} star{"s" if stars != 1 else ""}!')
    
    return redirect('resources:resource_detail', pk=pk)


@login_required
def add_comment(request, pk):
    """Add a comment to a resource"""
    resource = get_object_or_404(Resource, pk=pk)
    
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

