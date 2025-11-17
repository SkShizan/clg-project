# FILE: attendance_app/admin.py

from django.contrib import admin
from .models import Department, Role, Employee, Attendance, LeaveRequest

# We are registering our four models here so they
# appear in the Django admin dashboard.

admin.site.register(Department)
admin.site.register(Role)
admin.site.register(Employee)
admin.site.register(Attendance)
admin.site.register(LeaveRequest)