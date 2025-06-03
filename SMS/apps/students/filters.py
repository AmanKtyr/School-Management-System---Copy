import django_filters
from .models import Student

class StudentFilter(django_filters.FilterSet):
    class Meta:
        model = Student
        fields = ['current_class', 'section']  # Add more fields if needed
