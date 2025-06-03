from django import template

register = template.Library()

@register.filter
def percentage(value, total):
    """Calculate percentage of value out of total"""
    if total == 0:
        return 0
    return int((value / total) * 100)
