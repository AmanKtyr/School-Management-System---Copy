from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.db.models import Q
from django.http import HttpResponse, JsonResponse
from django.utils import timezone
from django.contrib.contenttypes.models import ContentType

from apps.students.models import Student
from apps.staffs.models import Staff
from apps.exams.models import Exam

from .models import (
    DocumentCategory, DocumentType, Document,
    StudentDocument, StaffDocument, ExamDocument,
    DocumentTemplate
)
from .forms import (
    DocumentCategoryForm, DocumentTypeForm, DocumentForm,
    StudentDocumentForm, StaffDocumentForm, ExamDocumentForm,
    DocumentTemplateForm, DocumentUploadForm, DocumentSearchForm
)

# Create your views here.

@login_required
def document_dashboard(request):
    """Main dashboard for document management"""
    # Get counts for dashboard cards
    student_docs_count = StudentDocument.objects.count()
    staff_docs_count = StaffDocument.objects.count()
    exam_docs_count = ExamDocument.objects.count()
    general_docs_count = Document.objects.filter(
        content_type__isnull=True
    ).count()

    # Get recent documents
    recent_documents = Document.objects.all().order_by('-created_at')[:10]

    # Get document statistics
    document_stats = {
        'total_documents': Document.objects.count(),
        'approved_documents': Document.objects.filter(status='approved').count(),
        'pending_documents': Document.objects.filter(status='pending').count(),
        'expired_documents': Document.objects.filter(status='expired').count(),
    }

    context = {
        'student_docs_count': student_docs_count,
        'staff_docs_count': staff_docs_count,
        'exam_docs_count': exam_docs_count,
        'general_docs_count': general_docs_count,
        'recent_documents': recent_documents,
        'document_stats': document_stats,
        'document_types': DocumentType.objects.all(),
    }

    return render(request, 'documents/dashboard.html', context)

# Document Category Views
class DocumentCategoryListView(LoginRequiredMixin, ListView):
    model = DocumentCategory
    template_name = 'documents/category_list.html'
    context_object_name = 'categories'

class DocumentCategoryCreateView(LoginRequiredMixin, CreateView):
    model = DocumentCategory
    form_class = DocumentCategoryForm
    template_name = 'documents/category_form.html'
    success_url = reverse_lazy('documents:category_list')

    def form_valid(self, form):
        messages.success(self.request, 'Document category created successfully!')
        return super().form_valid(form)

class DocumentCategoryUpdateView(LoginRequiredMixin, UpdateView):
    model = DocumentCategory
    form_class = DocumentCategoryForm
    template_name = 'documents/category_form.html'
    success_url = reverse_lazy('documents:category_list')

    def form_valid(self, form):
        messages.success(self.request, 'Document category updated successfully!')
        return super().form_valid(form)

class DocumentCategoryDeleteView(LoginRequiredMixin, DeleteView):
    model = DocumentCategory
    template_name = 'documents/category_confirm_delete.html'
    success_url = reverse_lazy('documents:category_list')

    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Document category deleted successfully!')
        return super().delete(request, *args, **kwargs)

# Document Type Views
class DocumentTypeListView(LoginRequiredMixin, ListView):
    model = DocumentType
    template_name = 'documents/type_list.html'
    context_object_name = 'document_types'

class DocumentTypeCreateView(LoginRequiredMixin, CreateView):
    model = DocumentType
    form_class = DocumentTypeForm
    template_name = 'documents/type_form.html'
    success_url = reverse_lazy('documents:type_list')

    def form_valid(self, form):
        messages.success(self.request, 'Document type created successfully!')
        return super().form_valid(form)

class DocumentTypeUpdateView(LoginRequiredMixin, UpdateView):
    model = DocumentType
    form_class = DocumentTypeForm
    template_name = 'documents/type_form.html'
    success_url = reverse_lazy('documents:type_list')

    def form_valid(self, form):
        messages.success(self.request, 'Document type updated successfully!')
        return super().form_valid(form)

class DocumentTypeDeleteView(LoginRequiredMixin, DeleteView):
    model = DocumentType
    template_name = 'documents/type_confirm_delete.html'
    success_url = reverse_lazy('documents:type_list')

    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Document type deleted successfully!')
        return super().delete(request, *args, **kwargs)

# Document Views
class DocumentListView(LoginRequiredMixin, ListView):
    model = Document
    template_name = 'documents/document_list.html'
    context_object_name = 'documents'
    paginate_by = 20

    def get_queryset(self):
        queryset = super().get_queryset()
        form = DocumentSearchForm(self.request.GET)

        if form.is_valid():
            search_query = form.cleaned_data.get('search_query')
            entity_type = form.cleaned_data.get('entity_type')
            document_type = form.cleaned_data.get('document_type')
            status = form.cleaned_data.get('status')
            date_from = form.cleaned_data.get('date_from')
            date_to = form.cleaned_data.get('date_to')

            if search_query:
                queryset = queryset.filter(
                    Q(title__icontains=search_query) |
                    Q(document_number__icontains=search_query) |
                    Q(description__icontains=search_query) |
                    Q(tags__icontains=search_query)
                )

            if entity_type:
                if entity_type == 'student':
                    student_content_type = ContentType.objects.get_for_model(Student)
                    queryset = queryset.filter(content_type=student_content_type)
                elif entity_type == 'staff':
                    staff_content_type = ContentType.objects.get_for_model(Staff)
                    queryset = queryset.filter(content_type=staff_content_type)
                elif entity_type == 'exam':
                    exam_content_type = ContentType.objects.get_for_model(Exam)
                    queryset = queryset.filter(content_type=exam_content_type)
                elif entity_type == 'general':
                    queryset = queryset.filter(content_type__isnull=True)

            if document_type:
                queryset = queryset.filter(document_type=document_type)

            if status:
                queryset = queryset.filter(status=status)

            if date_from:
                queryset = queryset.filter(created_at__gte=date_from)

            if date_to:
                queryset = queryset.filter(created_at__lte=date_to)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_form'] = DocumentSearchForm(self.request.GET)
        return context

class DocumentDetailView(LoginRequiredMixin, DetailView):
    model = Document
    template_name = 'documents/document_detail.html'
    context_object_name = 'document'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        document = self.get_object()

        # Get related entity if exists
        if document.content_type and document.object_id:
            content_type = document.content_type
            model_class = content_type.model_class()
            try:
                entity = model_class.objects.get(pk=document.object_id)
                context['entity'] = entity
                context['entity_type'] = content_type.model
            except model_class.DoesNotExist:
                pass

        return context

@login_required
def document_upload(request):
    """View for uploading documents"""
    if request.method == 'POST':
        form = DocumentUploadForm(request.POST, request.FILES)
        if form.is_valid():
            # Create the document
            document = Document(
                title=form.cleaned_data['title'],
                document_type=form.cleaned_data['document_type'],
                file=form.cleaned_data['file'],
                document_number=form.cleaned_data['document_number'],
                description=form.cleaned_data['description'],
                tags=form.cleaned_data['tags'],
                expiry_date=form.cleaned_data['expiry_date'],
                created_by=request.user.username,
                status='draft'
            )

            # Set content type and object id based on entity type
            entity_type = form.cleaned_data['entity_type']
            if entity_type == 'student':
                student = form.cleaned_data['student']
                if student:
                    document.content_type = ContentType.objects.get_for_model(Student)
                    document.object_id = student.id
            elif entity_type == 'staff':
                staff = form.cleaned_data['staff']
                if staff:
                    document.content_type = ContentType.objects.get_for_model(Staff)
                    document.object_id = staff.id
            elif entity_type == 'exam':
                exam = form.cleaned_data['exam']
                if exam:
                    document.content_type = ContentType.objects.get_for_model(Exam)
                    document.object_id = exam.id

            document.save()

            # Create the specific document relation
            if entity_type == 'student' and form.cleaned_data['student']:
                StudentDocument.objects.create(
                    student=form.cleaned_data['student'],
                    document=document
                )
            elif entity_type == 'staff' and form.cleaned_data['staff']:
                StaffDocument.objects.create(
                    staff=form.cleaned_data['staff'],
                    document=document
                )
            elif entity_type == 'exam' and form.cleaned_data['exam']:
                ExamDocument.objects.create(
                    exam=form.cleaned_data['exam'],
                    document=document
                )

            messages.success(request, 'Document uploaded successfully!')
            return redirect('documents:document_detail', pk=document.pk)
    else:
        form = DocumentUploadForm()

    context = {
        'form': form,
        'document_types': DocumentType.objects.all(),
    }

    return render(request, 'documents/document_upload.html', context)

class DocumentUpdateView(LoginRequiredMixin, UpdateView):
    model = Document
    form_class = DocumentForm
    template_name = 'documents/document_form.html'

    def form_valid(self, form):
        messages.success(self.request, 'Document updated successfully!')
        return super().form_valid(form)

class DocumentDeleteView(LoginRequiredMixin, DeleteView):
    model = Document
    template_name = 'documents/document_confirm_delete.html'
    success_url = reverse_lazy('documents:document_list')

    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Document deleted successfully!')
        return super().delete(request, *args, **kwargs)

@login_required
def document_download(request, pk):
    """View for downloading documents"""
    document = get_object_or_404(Document, pk=pk)

    # Update download count or log download activity here if needed

    response = HttpResponse(document.file, content_type='application/octet-stream')
    response['Content-Disposition'] = f'attachment; filename="{document.file.name.split("/")[-1]}"'
    return response

# Student Documents Views
@login_required
def student_documents(request, student_id=None):
    """View for student documents"""
    if student_id:
        student = get_object_or_404(Student, pk=student_id)
        documents = StudentDocument.objects.filter(student=student)
        context = {
            'student': student,
            'documents': documents,
        }
        return render(request, 'documents/student_documents.html', context)
    else:
        # Show all students with document counts
        students = Student.objects.filter(current_status='active')
        students_with_docs = []

        for student in students:
            doc_count = StudentDocument.objects.filter(student=student).count()
            students_with_docs.append({
                'student': student,
                'document_count': doc_count
            })

        context = {
            'students_with_docs': students_with_docs,
        }
        return render(request, 'documents/students_list.html', context)

# Staff Documents Views
@login_required
def staff_documents(request, staff_id=None):
    """View for staff documents"""
    if staff_id:
        staff = get_object_or_404(Staff, pk=staff_id)
        documents = StaffDocument.objects.filter(staff=staff)
        context = {
            'staff': staff,
            'documents': documents,
        }
        return render(request, 'documents/staff_documents.html', context)
    else:
        # Show all staff with document counts
        staffs = Staff.objects.filter(current_status='active')
        staffs_with_docs = []

        for staff in staffs:
            doc_count = StaffDocument.objects.filter(staff=staff).count()
            staffs_with_docs.append({
                'staff': staff,
                'document_count': doc_count
            })

        context = {
            'staffs_with_docs': staffs_with_docs,
        }
        return render(request, 'documents/staffs_list.html', context)

# Exam Documents Views
@login_required
def exam_documents(request, exam_id=None):
    """View for exam documents"""
    if exam_id:
        exam = get_object_or_404(Exam, pk=exam_id)
        documents = ExamDocument.objects.filter(exam=exam)
        context = {
            'exam': exam,
            'documents': documents,
        }
        return render(request, 'documents/exam_documents.html', context)
    else:
        # Show all exams with document counts
        exams = Exam.objects.all()
        exams_with_docs = []

        for exam in exams:
            doc_count = ExamDocument.objects.filter(exam=exam).count()
            exams_with_docs.append({
                'exam': exam,
                'document_count': doc_count
            })

        context = {
            'exams_with_docs': exams_with_docs,
        }
        return render(request, 'documents/exams_list.html', context)

# Document Template Views
class DocumentTemplateListView(LoginRequiredMixin, ListView):
    model = DocumentTemplate
    template_name = 'documents/template_list.html'
    context_object_name = 'templates'

class DocumentTemplateCreateView(LoginRequiredMixin, CreateView):
    model = DocumentTemplate
    form_class = DocumentTemplateForm
    template_name = 'documents/template_form.html'
    success_url = reverse_lazy('documents:template_list')

    def form_valid(self, form):
        messages.success(self.request, 'Document template created successfully!')
        return super().form_valid(form)

class DocumentTemplateUpdateView(LoginRequiredMixin, UpdateView):
    model = DocumentTemplate
    form_class = DocumentTemplateForm
    template_name = 'documents/template_form.html'
    success_url = reverse_lazy('documents:template_list')

    def form_valid(self, form):
        messages.success(self.request, 'Document template updated successfully!')
        return super().form_valid(form)

class DocumentTemplateDeleteView(LoginRequiredMixin, DeleteView):
    model = DocumentTemplate
    template_name = 'documents/template_confirm_delete.html'
    success_url = reverse_lazy('documents:template_list')

    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Document template deleted successfully!')
        return super().delete(request, *args, **kwargs)

@login_required
def document_template_download(request, pk):
    """View for downloading document templates"""
    template = get_object_or_404(DocumentTemplate, pk=pk)

    response = HttpResponse(template.file, content_type='application/octet-stream')
    response['Content-Disposition'] = f'attachment; filename="{template.file.name.split("/")[-1]}"'
    return response

# API Views
@login_required
def get_document_types(request):
    """API view to get document types based on entity type"""
    entity_type = request.GET.get('entity_type', '')

    if entity_type:
        document_types = DocumentType.objects.filter(entity_type=entity_type)
    else:
        document_types = DocumentType.objects.all()

    data = [{'id': dt.id, 'name': dt.name} for dt in document_types]
    return JsonResponse(data, safe=False)
