from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import OperationalError
from django.utils import timezone
from .models import Resource, Tag, Bookmark
from .forms import ResourceUploadForm
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
            
            resource.save()
            form.save_m2m()  # Save tags
            
            messages.success(request, 'Resource uploaded successfully! It is pending verification.')
            return redirect('resources:resource_detail', pk=resource.pk)
    else:
        form = ResourceUploadForm()
    
    return render(request, 'resources/resource_upload.html', {'form': form})


@login_required
def resource_detail(request, pk):
    """View a specific resource"""
    resource = get_object_or_404(Resource, pk=pk)
    
    # Increment view count
    resource.increment_view_count()
    
    # Check if user has bookmarked this resource
    is_bookmarked = False
    if request.user.is_authenticated:
        is_bookmarked = Bookmark.objects.filter(
            user=request.user, 
            resource=resource
        ).exists()
    
    context = {
        'resource': resource,
        'is_bookmarked': is_bookmarked,
    }
    return render(request, 'resources/resource_detail.html', context)


@login_required
def resource_list(request):
    """List all verified resources"""
    resources = Resource.objects.filter(verification_status='verified')
    
    # Filter by tags if provided
    tag_filter = request.GET.get('tag')
    if tag_filter:
        resources = resources.filter(tags__name=tag_filter)
    
    # Search functionality
    search_query = request.GET.get('q')
    if search_query:
        resources = resources.filter(
            title__icontains=search_query
        ) | resources.filter(
            description__icontains=search_query
        )
    
    context = {
        'resources': resources,
        'search_query': search_query,
        'tag_filter': tag_filter,
    }
    return render(request, 'resources/resource_list.html', context)


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

