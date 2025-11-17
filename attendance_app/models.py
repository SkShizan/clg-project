# FILE: attendance_app/models.py

from django.db import models
from django.contrib.auth.models import User

# Model 1: Department
# Stores company departments (e.g., Engineering, Sales, HR)
class Department(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

# Model 2: Role
# Stores job roles (e.g., Software Engineer, Manager)
class Role(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

# Model 3: Employee
# This model extends Django's built-in User model
class Employee(models.Model):
    # This links the Employee profile to a User login account
    # If the User is deleted, the associated Employee profile is also deleted
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    
    # Company-specific details
    employee_id = models.CharField(max_length=20, unique=True)
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, blank=True)
    role = models.ForeignKey(Role, on_delete=models.SET_NULL, null=True, blank=True)
    join_date = models.DateField()

    def __str__(self):
        # Show the user's full name if available, otherwise just their username
        return self.user.get_full_name() or self.user.username

# Model 4: Attendance
# This table will store every single attendance record
class Attendance(models.Model):
    
    STATUS_CHOICES = [
        ('PRESENT', 'Present'),
        ('ABSENT', 'Absent'),
        ('LEAVE', 'On Leave'),
    ]

    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    date = models.DateField()
    check_in = models.TimeField(null=True, blank=True)
    check_out = models.TimeField(null=True, blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='ABSENT')

    class Meta:
        # Ensures an employee can only have one attendance record per day
        unique_together = ('employee', 'date')

    def __str__(self):
        return f"{self.employee} - {self.date} ({self.status})"
    
    
class LeaveRequest(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('APPROVED', 'Approved'),
        ('REJECTED', 'Rejected'),
    ]

    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    start_date = models.DateField()
    end_date = models.DateField()
    reason = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='PENDING')
    created_at = models.DateTimeField(auto_now_add=True) # Automatically set when created
    
    class Meta:
        # Order by when they were created, newest first
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.employee} - {self.start_date} to {self.end_date} ({self.status})"