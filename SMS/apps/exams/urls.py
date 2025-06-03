from django.urls import path
from . import views

app_name = 'exams'

urlpatterns = [
    # Dashboard
    path('', views.exam_dashboard, name='dashboard'),
    # Guide
    path('guide/', views.exam_guide, name='exam_guide'),

    # Exam Types
    path('exam-types/', views.ExamTypeListView.as_view(), name='exam_type_list'),
    path('exam-types/create/', views.ExamTypeCreateView.as_view(), name='exam_type_create'),
    path('exam-types/<int:pk>/update/', views.ExamTypeUpdateView.as_view(), name='exam_type_update'),
    path('exam-types/<int:pk>/delete/', views.ExamTypeDeleteView.as_view(), name='exam_type_delete'),

    # Exams
    path('exams/', views.ExamListView.as_view(), name='exam_list'),
    path('exams/<int:pk>/', views.ExamDetailView.as_view(), name='exam_detail'),
    path('exams/create/', views.ExamCreateView.as_view(), name='exam_create'),
    path('exams/<int:pk>/update/', views.ExamUpdateView.as_view(), name='exam_update'),
    path('exams/<int:pk>/delete/', views.ExamDeleteView.as_view(), name='exam_delete'),

    # Exam Schedules
    path('schedules/', views.ExamScheduleListView.as_view(), name='exam_schedule_list'),
    path('schedules/create/', views.ExamScheduleCreateView.as_view(), name='exam_schedule_create'),
    path('schedules/<int:pk>/update/', views.ExamScheduleUpdateView.as_view(), name='exam_schedule_update'),
    path('schedules/<int:pk>/delete/', views.ExamScheduleDeleteView.as_view(), name='exam_schedule_delete'),

    # Question Papers
    path('question-papers/', views.QuestionPaperListView.as_view(), name='question_paper_list'),
    path('question-papers/create/', views.QuestionPaperCreateView.as_view(), name='question_paper_create'),
    path('question-papers/<int:pk>/update/', views.QuestionPaperUpdateView.as_view(), name='question_paper_update'),
    path('question-papers/<int:pk>/delete/', views.QuestionPaperDeleteView.as_view(), name='question_paper_delete'),
    path('question-papers/<int:pk>/download/', views.question_paper_download, name='question_paper_download'),

    # Admit Cards
    path('admit-cards/', views.AdmitCardListView.as_view(), name='admit_card_list'),
    path('admit-cards/generate/', views.admit_card_generate, name='admit_card_generate'),
    path('admit-cards/bulk-action/', views.admit_card_bulk_action, name='admit_card_bulk_action'),
    path('admit-cards/<int:pk>/view/', views.admit_card_view, name='admit_card_view'),
    path('admit-cards/<int:pk>/print/', views.admit_card_print, name='admit_card_print'),
    path('admit-cards/print-bulk/', views.admit_card_print_bulk, name='admit_card_print_bulk'),
    path('admit-cards/<int:pk>/delete/', views.AdmitCardDeleteView.as_view(), name='admit_card_delete'),

    # Marks Entry
    path('marks/', views.marks_entry, name='marks_entry'),
    path('marks/save/', views.marks_save, name='marks_save'),
    path('marks/import/', views.marks_import, name='marks_import'),

    # Results
    path('results/', views.ResultsListView.as_view(), name='results'),
    path('results/<int:pk>/', views.result_detail, name='result_detail'),
    path('results/<int:pk>/print/', views.result_print, name='result_print'),
    path('results/print-bulk/', views.result_print_bulk, name='result_print_bulk'),
    path('results/<int:pk>/publish/', views.result_publish, name='result_publish'),

    # Report Cards
    path('report-cards/<int:student_id>/<int:exam_id>/', views.report_card, name='report_card'),

    # Document Management
    path('documents/', views.document_management, name='document_management'),
    path('documents/archive/', views.document_archive, name='document_archive'),
    path('documents/generate/<str:doc_type>/', views.document_generate, name='document_generate'),
    path('documents/download/<str:doc_type>/<int:doc_id>/', views.document_download, name='document_download'),

    # API Endpoints for AJAX
    path('api/get-subjects/<int:class_id>/', views.get_subjects, name='get_subjects'),
    path('api/get-students/<int:class_id>/<str:section>/', views.get_students, name='get_students'),
    path('api/get-exam-details/<int:exam_id>/', views.get_exam_details, name='get_exam_details'),
]
