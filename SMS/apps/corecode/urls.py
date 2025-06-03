from django.urls import path
from . import views
from .views import (
    ClassCreateView,
    ClassDeleteView,
    ClassListView,
    CurrentSessionAndTermView,
    IndexView,
    SessionCreateView,
    SessionDeleteView,
    SessionListView,
    SubjectCreateView,
    SubjectDeleteView,
    SubjectListView,
    SubjectUpdateView,
    TermCreateView,
    TermDeleteView,
    TermListView,
)

urlpatterns = [
    path("", IndexView.as_view(), name="home"),
    path("site-config", views.site_config_view, name="configs"),  # Corrected view
    path(
        "current-session/", CurrentSessionAndTermView.as_view(), name="current-session"
    ),
    path("session/list/", SessionListView.as_view(), name="sessions"),
    path("session/create/", SessionCreateView.as_view(), name="session-create"),
    path(
        "session/<int:pk>/delete/",
        SessionDeleteView.as_view(),
        name="session-delete",
    ),
    path("term/list/", TermListView.as_view(), name="terms"),
    path("term/create/", TermCreateView.as_view(), name="term-create"),
    path("term/<int:pk>/delete/", TermDeleteView.as_view(), name="term-delete"),
    path("class/list/", ClassListView.as_view(), name="classes"),
    path("class/create/", ClassCreateView.as_view(), name="class-create"),
    path("class/<int:pk>/delete/", ClassDeleteView.as_view(), name="class-delete"),
    path("subject/list/", SubjectListView.as_view(), name="subjects"),
    path("subject/create/", SubjectCreateView.as_view(), name="subject-create"),
    path(
        "subject/<int:pk>/update/",
        SubjectUpdateView.as_view(),
        name="subject-update",
    ),
    path(
        "subject/<int:pk>/delete/",
        SubjectDeleteView.as_view(),
        name="subject-delete",
    ),
    path('siteconfig/', views.site_config_view, name='siteconfig'),
    path("college-profile/", views.college_profile_view, name="college-profile"),
    path('site-config/', views.site_config_view, name='site_config'),
    path('college-profile/', views.college_profile_view, name='college_profile'),
    path("fees/settings/", views.fee_settings, name="fee_settings"),
    path('api/get-fee-settings/<int:class_id>/<str:section>/', views.get_fee_settings, name='get_fee_settings'),
    path('fees/settings/list/', views.fee_settings_list, name='fee_settings_list'),
    path('api/get-sections/<int:class_id>/', views.get_sections_by_class, name='get_sections_by_class'),
    path('api/class/<int:class_id>/update/', views.update_class_ajax, name='update_class_ajax'),
    path('api/session/<int:session_id>/update/', views.update_session_ajax, name='update_session_ajax'),
    path('api/term/<int:term_id>/update/', views.update_term_ajax, name='update_term_ajax'),
    path('api/classes/', views.get_all_classes, name='get_all_classes'),
    path('api/teachers/', views.get_all_teachers, name='get_all_teachers'),
    path('api/all-assignments/', views.get_all_assignments, name='get_all_assignments'),
    path('api/class/<int:class_id>/subjects/', views.get_class_subjects, name='get_class_subjects'),
    path('api/assign-subject/', views.assign_subject_to_class, name='assign_subject_to_class'),
    path('api/remove-subject/<int:class_subject_id>/', views.remove_subject_from_class, name='remove_subject_from_class'),
    path('class/<int:class_id>/data/', views.get_class_data, name='get_class_data'),
    path('subject/<int:subject_id>/data/', views.get_subject_data, name='get_subject_data'),
    path('subject/<int:subject_id>/update-ajax/', views.update_subject_ajax, name='update_subject_ajax'),
    path('subject/<int:subject_id>/exams/', views.get_subject_exams, name='get_subject_exams'),
    path('logout/', views.custom_logout_view, name='logout'),

    # System Settings URLs
    path('system-settings/', views.system_settings_dashboard, name='system_settings_dashboard'),
    path('system-settings/general/', views.general_settings, name='general_settings'),
    path('system-settings/academic/', views.academic_settings, name='academic_settings'),
    path('system-settings/database/', views.database_management, name='database_management'),
    path('system-settings/backup-restore/', views.backup_restore, name='backup_restore'),
    path('system-settings/user-permissions/', views.user_permissions, name='user_permissions'),
    path('system-settings/security-logs/', views.security_logs, name='security_logs'),

    # Class Teacher API endpoints
    path('api/class-teachers/', views.get_class_teachers, name='get_class_teachers'),
    path('api/class/<int:class_id>/teacher/', views.get_class_teacher, name='get_class_teacher'),
    path('api/class/<int:class_id>/section/<str:section>/teacher/', views.get_class_teacher, name='get_class_section_teacher'),
    path('api/assign-class-teacher/', views.assign_class_teacher, name='assign_class_teacher'),
    path('api/remove-class-teacher/<int:class_teacher_id>/', views.remove_class_teacher, name='remove_class_teacher'),

    # Section API endpoints
    path('api/sections/', views.get_all_sections, name='get_all_sections'),
    path('api/class/<int:class_id>/sections/', views.get_class_sections, name='get_class_sections'),
    path('api/add-section/', views.add_section, name='add_section'),
    path('api/update-section/<int:section_id>/', views.update_section, name='update_section'),
    path('api/delete-section/<int:section_id>/', views.delete_section, name='delete_section'),

    # Backup & Restore API endpoints
    path('api/create-backup/', views.create_backup_ajax, name='create_backup_ajax'),
    path('api/restore-backup/<int:backup_id>/', views.restore_backup_ajax, name='restore_backup_ajax'),
    path('api/delete-backup/<int:backup_id>/', views.delete_backup_ajax, name='delete_backup_ajax'),
    path('api/download-backup/<int:backup_id>/', views.download_backup_ajax, name='download_backup_ajax'),
    path('api/save-automated-backup-settings/', views.save_automated_backup_settings, name='save_automated_backup_settings'),
]
