from django import template
from django.urls import reverse

# Create a library instance
register = template.Library()

@register.simple_tag(takes_context=True)
def get_breadcrumb_icon(context, url_name):
    """
    Returns an appropriate icon class based on the URL name
    """
    icon_mapping = {
        'home': 'fas fa-home',
        'student-list': 'fas fa-user-graduate',
        'student-create': 'fas fa-user-plus',
        'student-detail': 'fas fa-info-circle',
        'staff-list': 'fas fa-chalkboard-teacher',
        'staff-create': 'fas fa-user-plus',
        'staff-detail': 'fas fa-info-circle',
        'non-teaching-staffs-list': 'fas fa-users',
        'non-teaching-staffs-create': 'fas fa-user-plus',
        'non-teaching-staffs-detail': 'fas fa-info-circle',
        'classes': 'fas fa-school',
        'subjects': 'fas fa-book',
        'sessions': 'fas fa-calendar-alt',
        'terms': 'fas fa-clock',
        'fee_settings': 'fas fa-money-bill-wave',
        'fee_settings_list': 'fas fa-list',
        'configs': 'fas fa-cog',
        'attendance_list': 'fas fa-calendar-check',
        'create-result': 'fas fa-clipboard-list',
        'view-results': 'fas fa-eye',
    }

    return icon_mapping.get(url_name, 'fas fa-link')

@register.simple_tag(takes_context=True)
def get_breadcrumb_title(context, url_name):
    """
    Returns a formatted title based on the URL name
    """
    title_mapping = {
        'home': 'Home',
        'student-list': 'Student List',
        'student-create': 'Add Student',
        'student-detail': 'Student Details',
        'staff-list': 'Teaching Staff',
        'staff-create': 'Add Staff',
        'staff-detail': 'Staff Details',
        'non-teaching-staffs-list': 'Non-Teaching Staff',
        'non-teaching-staffs-create': 'Add Staff',
        'non-teaching-staffs-detail': 'Staff Details',
        'classes': 'Classes',
        'subjects': 'Subjects',
        'sessions': 'Academic Sessions',
        'terms': 'Academic Terms',
        'fee_settings': 'Fee Settings',
        'fee_settings_list': 'Fee Structure',
        'configs': 'System Settings',
        'attendance_list': 'Attendance',
        'create-result': 'Create Results',
        'view-results': 'View Results',
    }

    # If not in mapping, format the URL name by replacing hyphens with spaces and capitalizing
    return title_mapping.get(url_name, url_name.replace('-', ' ').title())

@register.inclusion_tag('includes/breadcrumb.html', takes_context=True)
def render_breadcrumb(context, current_page, parent_url=None, parent_title=None):
    """
    Renders a breadcrumb with the current page and optional parent page

    Usage:
    {% load breadcrumb_tags %}
    {% render_breadcrumb current_page="Student Details" parent_url="student-list" parent_title="Student List" %}
    """
    items = []

    if parent_url and parent_title:
        items.append({
            'url': reverse(parent_url) if parent_url else '#',
            'title': parent_title,
            'icon': get_breadcrumb_icon(context, parent_url) if parent_url else None
        })

    return {
        'items': items,
        'current_page': current_page,
        'current_icon': None  # The JavaScript will add appropriate icons
    }
