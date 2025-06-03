from django.urls import path
from . import views

urlpatterns = [
    path('', views.transport_list, name='transport_list'),
]
