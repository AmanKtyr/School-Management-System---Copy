from django.urls import path
from .views import account_dashboard

urlpatterns = [
    path('dashboard/', account_dashboard, name='account_dashboard'),
]
