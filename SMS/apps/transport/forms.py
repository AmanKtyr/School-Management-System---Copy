from django import forms
from .models import Bus, Route, Driver, Assignment

class BusForm(forms.ModelForm):
    def clean_capacity(self):
        capacity = self.cleaned_data.get('capacity')
        if capacity is not None and capacity <= 0:
            raise forms.ValidationError('Capacity must be a positive number.')
        return capacity

    class Meta:
        model = Bus
        fields = ['number', 'capacity', 'status']
        widgets = {
            'number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Bus Number/Name'}),
            'capacity': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Capacity', 'min': 1}),
            'status': forms.Select(attrs={'class': 'form-control'}),
        }
        help_texts = {
            'number': 'Enter the bus number or name.',
            'capacity': 'Total seating capacity.',
        }
        labels = {
            'number': 'Bus Number/Name',
            'capacity': 'Capacity',
            'status': 'Status',
        }

class RouteForm(forms.ModelForm):
    def clean(self):
        cleaned_data = super().clean()
        start = cleaned_data.get('start_point')
        end = cleaned_data.get('end_point')
        if start and end and start == end:
            raise forms.ValidationError('Start and End points must be different.')
        return cleaned_data

    class Meta:
        model = Route
        fields = ['name', 'start_point', 'end_point', 'status']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Route Name'}),
            'start_point': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Start Point'}),
            'end_point': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'End Point'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
        }
        help_texts = {
            'name': 'Enter a name for the route.',
        }
        labels = {
            'name': 'Route Name',
            'start_point': 'Start Point',
            'end_point': 'End Point',
            'status': 'Status',
        }

class DriverForm(forms.ModelForm):
    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        if phone and not phone.isdigit():
            raise forms.ValidationError('Phone number must contain only digits.')
        return phone

    class Meta:
        model = Driver
        fields = ['name', 'phone', 'license_number', 'status']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Driver Name'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Phone Number'}),
            'license_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'License Number'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
        }
        labels = {
            'name': 'Driver Name',
            'phone': 'Phone',
            'license_number': 'License Number',
            'status': 'Status',
        }

class AssignmentForm(forms.ModelForm):
    def clean(self):
        cleaned_data = super().clean()
        bus = cleaned_data.get('bus')
        route = cleaned_data.get('route')
        if bus and route and bus.status != 'Active':
            raise forms.ValidationError('Selected bus is not active.')
        if bus and route and route.status != 'Active':
            raise forms.ValidationError('Selected route is not active.')
        return cleaned_data

    class Meta:
        model = Assignment
        fields = ['student_name', 'bus', 'route', 'status']
        widgets = {
            'student_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Student Name'}),
            'bus': forms.Select(attrs={'class': 'form-control'}),
            'route': forms.Select(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
        }
        labels = {
            'student_name': 'Student Name',
            'bus': 'Bus',
            'route': 'Route',
            'status': 'Status',
        }
