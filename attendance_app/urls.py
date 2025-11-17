# FILE: attendance_app/urls.py

from django.urls import path
from . import views
from django.contrib.auth.views import LoginView

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    
    # Auth URLs
    path('login/', LoginView.as_view(template_name='attendance_app/login.html'), name='login'),
    path('logout/', views.logout_view, name='logout'),

    # Action URLs
    path('check_in/', views.check_in, name='check_in'),
    path('check_out/', views.check_out, name='check_out'),

    # NEW Leave Request URL
    path('leave-request/', views.leave_request, name='leave_request'),

    # Admin URL
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('manage-leave/', views.manage_leave_requests, name='manage_leave_requests'),
    path('update-leave/<int:request_id>/<str:new_status>/', 
         views.update_leave_status, name='update_leave_status'),
    path('add-employee/', views.add_employee, name='add_employee'),
    path('edit-employee/<int:employee_id>/', views.edit_employee, name='edit_employee'),
    path('delete-employee/<int:employee_id>/', views.delete_employee, name='delete_employee'),
    path('employees/', views.employee_list, name='employee_list'),
]