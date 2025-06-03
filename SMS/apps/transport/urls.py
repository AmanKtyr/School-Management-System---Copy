from django.urls import path
from . import views

urlpatterns = [
    path('', views.transport_list, name='transport_list'),
    # Bus CRUD
    path('bus/add/', views.bus_add, name='bus_add'),
    path('bus/<int:pk>/edit/', views.bus_edit, name='bus_edit'),
    path('bus/<int:pk>/delete/', views.bus_delete, name='bus_delete'),
    # Route CRUD
    path('route/add/', views.route_add, name='route_add'),
    path('route/<int:pk>/edit/', views.route_edit, name='route_edit'),
    path('route/<int:pk>/delete/', views.route_delete, name='route_delete'),
    # Driver CRUD
    path('driver/add/', views.driver_add, name='driver_add'),
    path('driver/<int:pk>/edit/', views.driver_edit, name='driver_edit'),
    path('driver/<int:pk>/delete/', views.driver_delete, name='driver_delete'),
    # Assignment CRUD
    path('assignment/add/', views.assignment_add, name='assignment_add'),
    path('assignment/<int:pk>/edit/', views.assignment_edit, name='assignment_edit'),
    path('assignment/<int:pk>/delete/', views.assignment_delete, name='assignment_delete'),
]
