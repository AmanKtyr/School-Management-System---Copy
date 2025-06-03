from django.urls import path
from . import views

app_name = 'documents'

urlpatterns = [
    # Dashboard
    path('', views.document_dashboard, name='dashboard'),
    
    # Document Categories
    path('categories/', views.DocumentCategoryListView.as_view(), name='category_list'),
    path('categories/create/', views.DocumentCategoryCreateView.as_view(), name='category_create'),
    path('categories/<int:pk>/update/', views.DocumentCategoryUpdateView.as_view(), name='category_update'),
    path('categories/<int:pk>/delete/', views.DocumentCategoryDeleteView.as_view(), name='category_delete'),
    
    # Document Types
    path('types/', views.DocumentTypeListView.as_view(), name='type_list'),
    path('types/create/', views.DocumentTypeCreateView.as_view(), name='type_create'),
    path('types/<int:pk>/update/', views.DocumentTypeUpdateView.as_view(), name='type_update'),
    path('types/<int:pk>/delete/', views.DocumentTypeDeleteView.as_view(), name='type_delete'),
    
    # Documents
    path('list/', views.DocumentListView.as_view(), name='document_list'),
    path('<int:pk>/', views.DocumentDetailView.as_view(), name='document_detail'),
    path('upload/', views.document_upload, name='document_upload'),
    path('<int:pk>/update/', views.DocumentUpdateView.as_view(), name='document_update'),
    path('<int:pk>/delete/', views.DocumentDeleteView.as_view(), name='document_delete'),
    path('<int:pk>/download/', views.document_download, name='document_download'),
    
    # Student Documents
    path('students/', views.student_documents, name='student_documents'),
    path('students/<int:student_id>/', views.student_documents, name='student_documents_detail'),
    
    # Staff Documents
    path('staff/', views.staff_documents, name='staff_documents'),
    path('staff/<int:staff_id>/', views.staff_documents, name='staff_documents_detail'),
    
    # Exam Documents
    path('exams/', views.exam_documents, name='exam_documents'),
    path('exams/<int:exam_id>/', views.exam_documents, name='exam_documents_detail'),
    
    # Document Templates
    path('templates/', views.DocumentTemplateListView.as_view(), name='template_list'),
    path('templates/create/', views.DocumentTemplateCreateView.as_view(), name='template_create'),
    path('templates/<int:pk>/update/', views.DocumentTemplateUpdateView.as_view(), name='template_update'),
    path('templates/<int:pk>/delete/', views.DocumentTemplateDeleteView.as_view(), name='template_delete'),
    path('templates/<int:pk>/download/', views.document_template_download, name='template_download'),
    
    # API Endpoints
    path('api/document-types/', views.get_document_types, name='api_document_types'),
]
