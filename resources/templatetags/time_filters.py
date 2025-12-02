from django import template
from django.utils import timezone
from datetime import datetime

register = template.Library()

@register.filter(name='short_timesince')
def short_timesince(value):
    """
    Returns a shortened time since format.
    Examples: 5m, 2h, 3d, 1mo, 2y
    """
    if not value:
        return ''
    
    now = timezone.now()
    if timezone.is_aware(value):
        diff = now - value
    else:
        # Make value timezone-aware if it isn't
        if isinstance(value, datetime):
            value = timezone.make_aware(value)
        diff = now - value
    
    seconds = diff.total_seconds()
    
    if seconds < 60:
        return 'now'
    elif seconds < 3600:  # Less than 1 hour
        minutes = int(seconds / 60)
        return f'{minutes}m'
    elif seconds < 86400:  # Less than 1 day
        hours = int(seconds / 3600)
        return f'{hours}h'
    elif seconds < 2592000:  # Less than 30 days
        days = int(seconds / 86400)
        return f'{days}d'
    elif seconds < 31536000:  # Less than 365 days
        months = int(seconds / 2592000)
        return f'{months}mo'
    else:
        years = int(seconds / 31536000)
        return f'{years}y'
