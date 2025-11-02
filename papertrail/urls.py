"""
URL configuration for PaperTrail project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.shortcuts import render, redirect
from django.conf import settings
from django.conf.urls.static import static


def home_view(request):
    """
    Home view that redirects authenticated users to dashboard,
    and shows landing page (base.html) to anonymous users.
    """
    if request.user.is_authenticated:
        return redirect('accounts:dashboard')
    return render(request, 'base.html')


urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls')),
    path('resources/', include('resources.urls')),
    path('quizzes/', include('quizzes.urls')),
    path('flashcards/', include('flashcards.urls')),
    path('', home_view, name='home'),  # Custom home view with authentication check
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
