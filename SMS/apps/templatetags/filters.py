from django import template

from students.models import (
    Student,
    current_class,
    Section
)
register = template.Library()

@register.inclusion_tag('dropdown_filter.html')
def class_section_filter():
    classes = current_class.objects.all()  
    sections = Section.objects.all()  
    return {'classes': classes, 'sections': sections}
