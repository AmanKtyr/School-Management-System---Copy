from django.shortcuts import render
from django.contrib.auth.decorators import login_required

@login_required
def account_dashboard(request):
    return render(request, 'AccountDashboard/dashboard.html')
