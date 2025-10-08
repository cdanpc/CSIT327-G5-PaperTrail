from django.shortcuts import render
from .models import Resource
from django.db import OperationalError # Import the error

# --- General Views ---

def home(request):
    """Home page showing recent resources"""
    
    recent_resources = []
    popular_resources = []
    
    context = {
        'recent_resources': recent_resources,
        'popular_resources': popular_resources,
    }
    return render(request, 'resources/home.html', context)
