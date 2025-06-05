from django.db import models

STATUS_CHOICES = [
    ('Active', 'Active'),
    ('Inactive', 'Inactive'),
]

# Create your models here.

class Bus(models.Model):
    number = models.CharField(max_length=20)
    capacity = models.PositiveIntegerField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Active')

    def __str__(self):
        return self.number

class Route(models.Model):
    name = models.CharField(max_length=100)
    start_point = models.CharField(max_length=100)
    end_point = models.CharField(max_length=100)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Active')

    def __str__(self):
        return self.name

class Driver(models.Model):
    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=20)
    license_number = models.CharField(max_length=50)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Active')

    def __str__(self):
        return self.name

class Assignment(models.Model):
    student_name = models.CharField(max_length=100)
    bus = models.ForeignKey(Bus, on_delete=models.CASCADE)
    route = models.ForeignKey(Route, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Assigned')

    def __str__(self):
        return f"{self.student_name} - {self.bus.number}"
