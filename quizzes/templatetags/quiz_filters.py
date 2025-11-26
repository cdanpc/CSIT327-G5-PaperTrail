from django import template

register = template.Library()


@register.filter
def num_to_letter(value):
    """Converts a number to a letter (1 -> A, 2 -> B, 3 -> C, etc.)"""
    try:
        num = int(value)
        if 1 <= num <= 26:
            return chr(64 + num)
        return str(value)
    except (ValueError, TypeError):
        return str(value)


@register.filter
def chr_filter(value):
    """Convert a number to its ASCII character equivalent.
    Used to convert 1->A, 2->B, 3->C, 4->D, etc."""
    try:
        return chr(int(value) + 64)
    except (ValueError, TypeError):
        return value
