from django.urls import path
from . import views

app_name = 'notice'

urlpatterns = [
    # Notice CRUD operations
    path('', views.NoticeListView.as_view(), name='list'),
    path('create/', views.NoticeCreateView.as_view(), name='create'),
    path('<int:pk>/', views.NoticeDetailView.as_view(), name='detail'),
    path('<int:pk>/edit/', views.NoticeUpdateView.as_view(), name='update'),
    path('<int:pk>/delete/', views.NoticeDeleteView.as_view(), name='delete'),

    # Quick notice creation
    path('quick-create/', views.quick_notice_create, name='quick_create'),

    # User-specific views
    path('my-notices/', views.my_notices, name='my_notices'),
    path('dashboard/', views.dashboard_notices, name='dashboard'),

    # AJAX endpoints
    path('<int:notice_id>/mark-read/', views.mark_notice_read, name='mark_read'),

    # Category management
    path('categories/', views.NoticeCategoryListView.as_view(), name='category_list'),
    path('categories/create/', views.NoticeCategoryCreateView.as_view(), name='category_create'),
]