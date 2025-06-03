from django.urls import path

from .views import (
    DownloadCSVViewdownloadcsv,
    StudentBulkUploadView,
    StudentCreateView,
    StudentDeleteView,
    StudentDetailView,
    StudentListView,
    StudentUpdateView,
    StudentUDISECreateView,
    StudentUDISEUpdateView,
    upload_student_documents,
    get_sections_for_class,
    create_udise_info,
)

urlpatterns = [
    path("list", StudentListView.as_view(), name="student-list"),
    path("<int:pk>/", StudentDetailView.as_view(), name="student-detail"),
    path("create/", StudentCreateView.as_view(), name="student-create"),
    path("<int:pk>/update/", StudentUpdateView.as_view(), name="student-update"),
    path("delete/<int:pk>/", StudentDeleteView.as_view(), name="student-delete"),
    path("upload/", StudentBulkUploadView.as_view(), name="student-upload"),
    path("download-csv/", DownloadCSVViewdownloadcsv.as_view(), name="download-csv"),
    path("<int:pk>/upload-documents/", upload_student_documents, name="upload-student-documents"),

    # UDISE+ style forms
    path("create-udise/", StudentUDISECreateView.as_view(), name="student-create-udise"),
    path("<int:pk>/update-udise/", StudentUDISEUpdateView.as_view(), name="student-update-udise"),
    path("<int:pk>/create-udise-info/", create_udise_info, name="create-udise-info"),

    # API endpoints
    path("api/class/<int:class_id>/sections/", get_sections_for_class, name="get-sections-for-class"),
]
