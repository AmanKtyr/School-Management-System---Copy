from django import forms
from .models import Bus, Route, Driver, Assignment

class BusForm(forms.ModelForm):
    class Meta:
        model = Bus
        fields = ['number', 'capacity', 'status']

class RouteForm(forms.ModelForm):
    class Meta:
        model = Route
        fields = ['name', 'start_point', 'end_point', 'status']

class DriverForm(forms.ModelForm):
    class Meta:
        model = Driver
        fields = ['name', 'phone', 'license_number', 'status']

class AssignmentForm(forms.ModelForm):
    class Meta:
        model = Assignment
        fields = ['student_name', 'bus', 'route', 'status']
