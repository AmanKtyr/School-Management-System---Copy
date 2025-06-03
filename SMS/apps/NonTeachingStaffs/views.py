from django.urls import reverse_lazy
from django.views.generic import DetailView, ListView, CreateView, UpdateView, DeleteView
from django.contrib.messages.views import SuccessMessageMixin
from django.forms import widgets
from .models import NonTeachingStaff  

# ✅ List View (Fixed Template Path)
class NonTeachingStaffsListView(ListView):
    model = NonTeachingStaff
    template_name = "non-teaching-staffs/non-teaching-staffs_list.html"  # Fixed

# ✅ Detail View (Fixed Template Path)
class NonTeachingStaffsDetailView(DetailView):
    model = NonTeachingStaff
    template_name = "non-teaching-staffs/non-teaching-staffs_detail.html"  # Fixed

# ✅ Create View (With Date Pickers)
class NonTeachingStaffsCreateView(SuccessMessageMixin, CreateView):
    model = NonTeachingStaff
    fields = "__all__"
    success_message = "New staff successfully added"
    template_name = "non-teaching-staffs/non-teaching-staffs_form.html"  # Fixed

    def get_form(self):
        form = super().get_form()
        form.fields["date_of_birth"].widget = widgets.DateInput(attrs={"type": "date"})
        form.fields["date_of_registration"].widget = widgets.DateInput(attrs={"type": "date"})
        form.fields["address"].widget = widgets.Textarea(attrs={"rows": 1})
        form.fields["others"].widget = widgets.Textarea(attrs={"rows": 1})
        return form

# ✅ Update View (With Date Pickers)
class NonTeachingStaffsUpdateView(SuccessMessageMixin, UpdateView):
    model = NonTeachingStaff
    fields = "__all__"
    success_message = "Record successfully updated."
    template_name = "non-teaching-staffs/non-teaching-staffs_form.html"  # Fixed

    def get_form(self):
        form = super().get_form()
        form.fields["date_of_birth"].widget = widgets.DateInput(attrs={"type": "date"})
        form.fields["date_of_registration"].widget = widgets.DateInput(attrs={"type": "date"})
        form.fields["address"].widget = widgets.Textarea(attrs={"rows": 1})
        return form

# ✅ Delete View (Added template_name for confirmation page)
class NonTeachingStaffsDeleteView(SuccessMessageMixin, DeleteView):
    model = NonTeachingStaff
    success_url = reverse_lazy("non-teaching-staffs-list")
    success_message = "Staff record successfully deleted."
    template_name = "non-teaching-staffs/non-teaching-staffs_confirm_delete.html"  # Fixed
