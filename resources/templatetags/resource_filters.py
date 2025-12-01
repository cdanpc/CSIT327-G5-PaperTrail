from django import template

register = template.Library()

@register.filter
def filesizeformat(bytes_size):
    """
    Format file size in bytes to human-readable format.
    Examples: 1024 -> "1 KB", 1048576 -> "1 MB"
    """
    if bytes_size is None:
        return "N/A"
    
    bytes_size = int(bytes_size)
    
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if bytes_size < 1024.0:
            if unit == 'B':
                return f"{bytes_size} {unit}"
            return f"{bytes_size:.2f} {unit}"
        bytes_size /= 1024.0
    
    return f"{bytes_size:.2f} PB"
