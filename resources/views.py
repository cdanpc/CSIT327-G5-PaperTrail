from django.shortcuts import render
from .models import Resource
from django.db import OperationalError # Import the error

# --- General Views ---

from django.shortcuts import redirect
from django.contrib import messages

def home(request):
    """Temporary redirect to dashboard with feature-in-progress message"""
    messages.info(request, 'The Resources feature is currently under development. Please check back soon!')
    return redirect('accounts:dashboard')
