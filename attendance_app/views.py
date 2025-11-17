# FILE: attendance_app/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.contrib import messages
from .models import Employee, Attendance, LeaveRequest, Department, Role
from datetime import date, datetime,timedelta
from django.contrib.auth.models import User
from .forms import LeaveRequestForm, AddEmployeeForm, EditEmployeeForm
from django.contrib.admin.views.decorators import staff_member_required

# --- Dashboard View (UPDATED) ---
@login_required
def dashboard(request):
    today = date.today()
    
    try:
        employee = request.user.employee
    except Employee.DoesNotExist:
        return render(request, 'attendance_app/dashboard_admin.html')

    # This part is the same
    attendance, created = Attendance.objects.get_or_create(
        employee=employee,
        date=today
    )
    
    # --- THIS IS THE NEW PART ---
    # Get all attendance records for this employee, ordered by most recent
    attendance_history = Attendance.objects.filter(employee=employee).order_by('-date')
    # --- END OF NEW PART ---

    # Add the history to our context
    context = {
        'employee': employee,
        'attendance': attendance,
        'attendance_history': attendance_history  # <-- NEW
    }
    return render(request, 'attendance_app/dashboard.html', context)

@staff_member_required # This decorator handles both login and staff status checks
def admin_dashboard(request):
    
    # Get the date from the URL, default to today if not provided
    query_date_str = request.GET.get('date', default=date.today().isoformat())
    
    try:
        # Convert the string from the URL into a date object
        selected_date = date.fromisoformat(query_date_str)
    except ValueError:
        # If the date format is bad, just default to today
        selected_date = date.today()

    # --- This is a key "pro" feature ---
    # Ensure every employee has an attendance record for the selected date
    # This guarantees all employees appear on the report, even if they're absent.
    all_employees = Employee.objects.all()
    for emp in all_employees:
        Attendance.objects.get_or_create(
            employee=emp,
            date=selected_date
            # It will use the model's default 'ABSENT' status if created
        )
    
    # Now, fetch all records for that day, pre-loading employee data for efficiency
    attendance_list = Attendance.objects.filter(
        date=selected_date
    ).select_related('employee', 'employee__user') # 'select_related' is a performance optimization

    context = {
        'attendance_list': attendance_list,
        'selected_date': selected_date,
    }
    return render(request, 'attendance_app/admin_dashboard.html', context)

# --- Check-in View (NEW) ---
@login_required
def check_in(request):
    if request.method == 'POST':
        employee = request.user.employee
        today = date.today()
        now = datetime.now().time()

        # Find today's attendance record
        attendance = get_object_or_404(Attendance, employee=employee, date=today)
        
        # Update the record
        if attendance.status == 'ABSENT':
            attendance.check_in = now
            attendance.status = 'PRESENT'
            attendance.save()
            messages.success(request, 'You have checked in successfully.')

    return redirect('dashboard')


# --- Check-out View (NEW) ---
@login_required
def check_out(request):
    if request.method == 'POST':
        employee = request.user.employee
        today = date.today()
        now = datetime.now().time()

        # Find today's attendance record
        attendance = get_object_or_404(Attendance, employee=employee, date=today)

        # Update the record
        if attendance.status == 'PRESENT' and attendance.check_out is None:
            attendance.check_out = now
            attendance.save()
            messages.success(request, 'You have checked out successfully.')

    return redirect('dashboard')


# --- Logout View (No Change) ---
def logout_view(request):
    logout(request)
    return redirect('login')


@login_required
def leave_request(request):
    employee = request.user.employee
    
    # Handle the form submission (POST)
    if request.method == 'POST':
        form = LeaveRequestForm(request.POST)
        if form.is_valid():
            # Don't save to DB yet. We need to add the employee.
            leave = form.save(commit=False)
            leave.employee = employee
            leave.save()
            messages.success(request, 'Your leave request has been submitted.')
            return redirect('dashboard') # Redirect to dashboard on success
    
    # Show the blank form (GET)
    else:
        form = LeaveRequestForm()

    # Also, fetch this employee's past leave requests to show on the page
    past_requests = LeaveRequest.objects.filter(employee=employee)

    context = {
        'form': form,
        'past_requests': past_requests
    }
    return render(request, 'attendance_app/leave_request.html', context)

@staff_member_required
def manage_leave_requests(request):
    # Get all requests that are still 'PENDING'
    pending_requests = LeaveRequest.objects.filter(status='PENDING').select_related('employee__user')
    
    context = {
        'pending_requests': pending_requests,
    }
    return render(request, 'attendance_app/manage_leave_requests.html', context)


# --- Admin: Approve/Reject Logic (NEW VIEW) ---
@staff_member_required
def update_leave_status(request, request_id, new_status):
    # This view handles the POST request from the button click
    if request.method != 'POST':
        return redirect('manage_leave_requests') # Only allow POST

    leave_request = get_object_or_404(LeaveRequest, id=request_id)

    if new_status == 'approve':
        leave_request.status = 'APPROVED'
        messages.success(request, f"Leave request for {leave_request.employee.user.username} approved.") # <-- ADD
        
        # --- This is the critical logic ---
        # Update attendance records for the approved dates
        current_date = leave_request.start_date
        while current_date <= leave_request.end_date:
            # Find or create an attendance record for this day
            attendance, created = Attendance.objects.get_or_create(
                employee=leave_request.employee,
                date=current_date
            )
            
            # Set its status to 'On Leave'
            attendance.status = 'LEAVE'
            attendance.check_in = None  # Clear any check-in/out times
            attendance.check_out = None
            attendance.save()
            
            # Move to the next day
            current_date += timedelta(days=1)
        # --- End of critical logic ---

    elif new_status == 'reject':
        leave_request.status = 'REJECTED'
        messages.warning(request, f"Leave request for {leave_request.employee.user.username} rejected.") # <-- ADD
    
    leave_request.save()
    return redirect('manage_leave_requests')


@staff_member_required
def add_employee(request):
    if request.method == 'POST':
        form = AddEmployeeForm(request.POST)
        if form.is_valid():
            # Form is valid, get the cleaned data
            data = form.cleaned_data
            
            # 1. Create the User object
            new_user = User.objects.create_user(
                username=data['username'],
                password=data['password'],
                first_name=data['first_name'],
                last_name=data['last_name']
            )
            
            # 2. Create the Employee object and link it to the user
            Employee.objects.create(
                user=new_user,
                employee_id=data['employee_id'],
                department=data['department'],
                role=data['role'],
                join_date=data['join_date']
            )
            
            # Redirect to the admin dashboard on success
            messages.success(request, f"Employee '{new_user.username}' created successfully.") # <-- ADD
            return redirect('admin_dashboard')
    else:
        # Show a blank form
        form = AddEmployeeForm()

    context = {
        'form': form
    }
    return render(request, 'attendance_app/add_employee.html', context)


@staff_member_required
def edit_employee(request, employee_id):
    # Get the employee object we want to edit
    employee = get_object_or_404(Employee, id=employee_id)
    user = employee.user
    
    if request.method == 'POST':
        # Pass the POST data and the user_instance to the form
        form = EditEmployeeForm(request.POST, user_instance=user)
        if form.is_valid():
            data = form.cleaned_data
            
            # --- Update the User object ---
            user.username = data['username']
            user.first_name = data['first_name']
            user.last_name = data['last_name']
            
            # Only update password if a new one was provided
            if data['password']:
                user.set_password(data['password'])
            
            user.save()
            
            # --- Update the Employee object ---
            employee.employee_id = data['employee_id']
            employee.department = data['department']
            employee.role = data['role']
            employee.join_date = data['join_date']
            employee.save()
            messages.success(request, f"Employee '{user.username}' updated successfully.") # <-- ADD
            
            return redirect('admin_dashboard')
    else:
        # --- Pre-populate the form with existing data ---
        initial_data = {
            'username': user.username,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'employee_id': employee.employee_id,
            'department': employee.department,
            'role': employee.role,
            'join_date': employee.join_date,
        }
        # Pass the initial data and the user_instance
        form = EditEmployeeForm(initial=initial_data, user_instance=user)

    context = {
        'form': form,
        'employee': employee
    }
    return render(request, 'attendance_app/edit_employee.html', context)

@staff_member_required
def delete_employee(request, employee_id):
    employee = get_object_or_404(Employee, id=employee_id)
    user = employee.user
    
    if request.method == 'POST':
        # This is the confirmation. Delete the user.
        # The Employee profile will be deleted automatically
        # because of the 'on_delete=models.CASCADE' in our model.
        user.delete()
        
        messages.success(request, f"Employee '{user.username}' has been permanently deleted.")
        return redirect('admin_dashboard')

    # This is the initial GET request. Show the confirmation page.
    context = {
        'employee': employee
    }
    return render(request, 'attendance_app/delete_employee.html', context)

@staff_member_required
def employee_list(request):
    # Get all employees. 
    # 'select_related' is a performance optimization that fetches the
    # related User, Department, and Role in a single database query.
    employees = Employee.objects.all().select_related(
        'user', 'department', 'role'
    ).order_by('user__last_name') # Order by last name
    
    context = {
        'employees': employees
    }
    return render(request, 'attendance_app/employee_list.html', context)