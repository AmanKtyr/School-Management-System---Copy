from django.shortcuts import render, redirect, get_object_or_404
from .models import Bus, Route, Driver, Assignment
from .forms import BusForm, RouteForm, DriverForm, AssignmentForm

# List view for all transport entities
def transport_list(request):
    buses = Bus.objects.all()
    routes = Route.objects.all()
    drivers = Driver.objects.all()
    assignments = Assignment.objects.all()
    return render(request, 'transport/transport_list.html', {
        'buses': buses,
        'routes': routes,
        'drivers': drivers,
        'assignments': assignments,
    })

# CRUD for Bus
def bus_add(request):
    if request.method == 'POST':
        form = BusForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('transport_list')
    else:
        form = BusForm()
    return render(request, 'transport/transport_form.html', {'form': form, 'title': 'Bus'})

def bus_edit(request, pk):
    bus = get_object_or_404(Bus, pk=pk)
    if request.method == 'POST':
        form = BusForm(request.POST, instance=bus)
        if form.is_valid():
            form.save()
            return redirect('transport_list')
    else:
        form = BusForm(instance=bus)
    return render(request, 'transport/transport_form.html', {'form': form, 'title': 'Bus'})

def bus_delete(request, pk):
    bus = get_object_or_404(Bus, pk=pk)
    bus.delete()
    return redirect('transport_list')

# CRUD for Route
def route_add(request):
    if request.method == 'POST':
        form = RouteForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('transport_list')
    else:
        form = RouteForm()
    return render(request, 'transport/transport_form.html', {'form': form, 'title': 'Route'})

def route_edit(request, pk):
    route = get_object_or_404(Route, pk=pk)
    if request.method == 'POST':
        form = RouteForm(request.POST, instance=route)
        if form.is_valid():
            form.save()
            return redirect('transport_list')
    else:
        form = RouteForm(instance=route)
    return render(request, 'transport/transport_form.html', {'form': form, 'title': 'Route'})

def route_delete(request, pk):
    route = get_object_or_404(Route, pk=pk)
    route.delete()
    return redirect('transport_list')

# CRUD for Driver
def driver_add(request):
    if request.method == 'POST':
        form = DriverForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('transport_list')
    else:
        form = DriverForm()
    return render(request, 'transport/transport_form.html', {'form': form, 'title': 'Driver'})

def driver_edit(request, pk):
    driver = get_object_or_404(Driver, pk=pk)
    if request.method == 'POST':
        form = DriverForm(request.POST, instance=driver)
        if form.is_valid():
            form.save()
            return redirect('transport_list')
    else:
        form = DriverForm(instance=driver)
    return render(request, 'transport/transport_form.html', {'form': form, 'title': 'Driver'})

def driver_delete(request, pk):
    driver = get_object_or_404(Driver, pk=pk)
    driver.delete()
    return redirect('transport_list')

# CRUD for Assignment
def assignment_add(request):
    if request.method == 'POST':
        form = AssignmentForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('transport_list')
    else:
        form = AssignmentForm()
    return render(request, 'transport/transport_form.html', {'form': form, 'title': 'Assignment'})

def assignment_edit(request, pk):
    assignment = get_object_or_404(Assignment, pk=pk)
    if request.method == 'POST':
        form = AssignmentForm(request.POST, instance=assignment)
        if form.is_valid():
            form.save()
            return redirect('transport_list')
    else:
        form = AssignmentForm(instance=assignment)
    return render(request, 'transport/transport_form.html', {'form': form, 'title': 'Assignment'})

def assignment_delete(request, pk):
    assignment = get_object_or_404(Assignment, pk=pk)
    assignment.delete()
    return redirect('transport_list')
