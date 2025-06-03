from django.contrib import admin
from .models import (
    DocumentCategory, DocumentType, Document,
    StudentDocument, StaffDocument, ExamDocument,
    DocumentTemplate
)

# Register your models here.
@admin.register(DocumentCategory)
class DocumentCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    search_fields = ('name',)

@admin.register(DocumentType)
class DocumentTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'entity_type', 'category', 'required')
    list_filter = ('entity_type', 'category', 'required')
    search_fields = ('name', 'description')

@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ('title', 'document_type', 'status', 'created_at', 'updated_at')
    list_filter = ('document_type', 'status')
    search_fields = ('title', 'document_number', 'description', 'tags')
    date_hierarchy = 'created_at'
    readonly_fields = ('created_at', 'updated_at')

@admin.register(StudentDocument)
class StudentDocumentAdmin(admin.ModelAdmin):
    list_display = ('student', 'document')
    list_filter = ('document__status',)
    search_fields = ('student__fullname', 'document__title')

@admin.register(StaffDocument)
class StaffDocumentAdmin(admin.ModelAdmin):
    list_display = ('staff', 'document')
    list_filter = ('document__status',)
    search_fields = ('staff__fullname', 'document__title')

@admin.register(ExamDocument)
class ExamDocumentAdmin(admin.ModelAdmin):
    list_display = ('exam', 'document')
    list_filter = ('document__status',)
    search_fields = ('exam__name', 'document__title')

@admin.register(DocumentTemplate)
class DocumentTemplateAdmin(admin.ModelAdmin):
    list_display = ('name', 'document_type', 'created_at', 'updated_at')
    list_filter = ('document_type',)
    search_fields = ('name', 'description')
    readonly_fields = ('created_at', 'updated_at')
