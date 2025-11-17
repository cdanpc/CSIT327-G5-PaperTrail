"""
Context processors for accounts app
"""
from django.contrib.auth import get_user_model
from resources.models import Resource, Bookmark
from quizzes.models import Quiz

User = get_user_model()

"""
def user_activity(request):
    Add user activity summary to context
    context = {}
    
    if request.user.is_authenticated:
        user = request.user
        
        # Get user's activity counts
        resources_uploaded = Resource.objects.filter(uploader=user).count()
        bookmarks_count = Bookmark.objects.filter(user=user).count()
    quizzes_created = Quiz.objects.filter(owner=user).count()
        
        # Get reviews written (verifications for professors)
        reviews_written = 0
        if user.is_professor:
            reviews_written = Resource.objects.filter(verification_by=user).count()
        
        context.update({
            'user_resources_uploaded': resources_uploaded,
            'user_bookmarks_count': bookmarks_count,
            'user_quizzes_created': quizzes_created,
            'user_reviews_written': reviews_written,
        })
    
    return context
"""