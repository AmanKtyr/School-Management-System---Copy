from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.auth.mixins import LoginRequiredMixin
from django.forms import widgets
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import DetailView, ListView
from django.views.generic.edit import CreateView, DeleteView, UpdateView
from django.http import JsonResponse
from django.contrib import messages
from functools import wraps

from .models import Staff


# Custom decorator to restrict access to admin users only
def admin_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_superuser:
            messages.error(request, "Access denied. Only administrators can access this page.")
            return render(request, '403.html', status=403)
        return view_func(request, *args, **kwargs)
    return _wrapped_view


# Custom mixin for class-based views to restrict access to admin users only
class AdminRequiredMixin:
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_superuser:
            messages.error(request, "Access denied. Only administrators can access this page.")
            return render(request, '403.html', status=403)
        return super().dispatch(request, *args, **kwargs)

class StaffListView(LoginRequiredMixin, AdminRequiredMixin, ListView):
    model = Staff

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Clear staff credentials from session if present
        if 'show_staff_credentials' in self.request.session:
            del self.request.session['show_staff_credentials']
        return context
class StaffDetailView(LoginRequiredMixin, AdminRequiredMixin, DetailView):
    model = Staff
    template_name = "staffs/staff_detail.html"
class StaffCreateView(LoginRequiredMixin, AdminRequiredMixin, SuccessMessageMixin, CreateView):
    model = Staff
    fields = "__all__"
    success_message = "New staff successfully added"

    def get_form(self):
        """add date picker in forms"""
        form = super(StaffCreateView, self).get_form()
        form.fields["date_of_birth"].widget = widgets.DateInput(attrs={"type": "date"})
        form.fields["date_of_registration"].widget = widgets.DateInput(
            attrs={"type": "date"}
        )
        form.fields["Subject_specification"].widget = widgets.Textarea(attrs={"rows": 1})
        form.fields["address"].widget = widgets.Textarea(attrs={"rows": 1})
        form.fields["others"].widget = widgets.Textarea(attrs={"rows": 1})
        return form

    def form_valid(self, form):
        """Override form_valid to handle login credentials popup"""
        response = super().form_valid(form)

        # Get the created staff object
        staff = self.object

        # Store credentials in session for popup display
        self.request.session['show_staff_credentials'] = {
            'staff_name': staff.fullname,
            'login_id': staff.staff_login_id,
            'password': staff.staff_password,
            'registration_number': staff.registration_number
        }

        return response

class StaffUpdateView(LoginRequiredMixin, AdminRequiredMixin, SuccessMessageMixin, UpdateView):
    model = Staff
    fields = "__all__"
    success_message = "Record successfully updated."

    def get_form(self):
        """add date picker in forms"""
        form = super(StaffUpdateView, self).get_form()
        form.fields["date_of_birth"].widget = widgets.DateInput(attrs={"type": "date"})
        form.fields["date_of_registration"].widget = widgets.DateInput(
            attrs={"type": "date"}
        )
        form.fields["Subject_specification"].widget = widgets.Textarea(attrs={"rows": 1})
        form.fields["address"].widget = widgets.Textarea(attrs={"rows": 1})
        form.fields["others"].widget = widgets.Textarea(attrs={"rows": 1})
        return form


class StaffDeleteView(LoginRequiredMixin, AdminRequiredMixin, DeleteView):
    model = Staff
    success_url = reverse_lazy("staff-list")
