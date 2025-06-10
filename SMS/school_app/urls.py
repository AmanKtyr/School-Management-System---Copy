"""newapp URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls.static import static
from django.urls import include, path

urlpatterns = [
    path("accounts/", include("django.contrib.auth.urls")),
    path("", include("apps.corecode.urls")),
    path("student/", include("apps.students.urls")),
    path('attendance/', include(('apps.attendance.urls', 'attendance'))),
    path("staff/", include("apps.staffs.urls")),
    # Finance app removed
    # Result app removed
    path("non-teaching-staffs/", include("apps.NonTeachingStaffs.urls")),
   # Added namespace
     path('fees/', include('apps.fees.urls', namespace='fees')),
    # Exams app
    path('exams/', include('apps.exams.urls', namespace='exams')),
    # Documents app
    path('documents/', include('apps.documents.urls', namespace='documents')),
    path('transport/', include('apps.transport.urls')),
    # Add dashboard apps
    path('student-dashboard/', include('StudentDashboard.urls')),
    path('teacher-dashboard/', include('TeacherDashboard.urls')),
    path('account-dashboard/', include('AccountDashboard.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
