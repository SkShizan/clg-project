# FILE: attendance_app/forms.py (NEW FILE)

from django import forms
from .models import LeaveRequest, Department, Role
from django.contrib.auth.models import User
from datetime import date

class LeaveRequestForm(forms.ModelForm):
    class Meta:
        model = LeaveRequest
        # We only want the user to fill out these 3 fields
        fields = ['start_date', 'end_date', 'reason']
        
        # Add Bootstrap's date picker widget to the date fields
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'end_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'reason': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    # This is professional validation. We add checks to make sure
    # the form data is logical before saving it.
    
    def clean_start_date(self):
        """Ensures the start date is not in the past."""
        start_date = self.cleaned_data.get('start_date')
        if start_date < date.today():
            raise forms.ValidationError("You cannot request leave for a past date.")
        return start_date

    def clean(self):
        """Ensures the end date is not before the start date."""
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')

        if start_date and end_date:
            if end_date < start_date:
                raise forms.ValidationError("End date cannot be before the start date.")
        return cleaned_data
    
    
# --- Add Employee Form (NEW) ---
class AddEmployeeForm(forms.Form):
    # --- User Fields ---
    username = forms.CharField(
        max_length=150, 
        required=True, 
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'}), 
        required=True
    )
    first_name = forms.CharField(
        max_length=100, 
        required=False, 
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    last_name = forms.CharField(
        max_length=100, 
        required=True, 
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    
    # --- Employee Fields ---
    employee_id = forms.CharField(
        max_length=20, 
        required=True, 
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    # This field gets its choices directly from the Department model
    department = forms.ModelChoiceField(
        queryset=Department.objects.all(), 
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    # This field gets its choices directly from the Role model
    role = forms.ModelChoiceField(
        queryset=Role.objects.all(), 
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    join_date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        required=True
    )

    # --- Validation ---
    def clean_username(self):
        """Check if the username is already taken."""
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("A user with this username already exists.")
        return username
    
    
class EditEmployeeForm(forms.Form):
    # --- User Fields ---
    username = forms.CharField(
        max_length=150, 
        required=True, 
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    # Password is now optional
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'}), 
        required=False,
        help_text="Leave blank to keep the current password."
    )
    first_name = forms.CharField(
        max_length=100, 
        required=False, 
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    last_name = forms.CharField(
        max_length=100, 
        required=True, 
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    
    # --- Employee Fields ---
    employee_id = forms.CharField(
        max_length=20, 
        required=True, 
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    department = forms.ModelChoiceField(
        queryset=Department.objects.all(), 
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    role = forms.ModelChoiceField(
        queryset=Role.objects.all(), 
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    join_date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        required=True
    )

    # We need to know which user we are editing to validate the username
    def __init__(self, *args, **kwargs):
        self.user_instance = kwargs.pop('user_instance', None)
        super(EditEmployeeForm, self).__init__(*args, **kwargs)

    def clean_username(self):
        """Check if the username is already taken by *another* user."""
        username = self.cleaned_data.get('username')
        
        if self.user_instance:
            # Check if a *different* user has this username
            if User.objects.filter(username=username).exclude(pk=self.user_instance.pk).exists():
                raise forms.ValidationError("A user with this username already exists.")
        elif User.objects.filter(username=username).exists():
            # Fallback for if user_instance wasn't passed
            raise forms.ValidationError("A user with this username already exists.")
        return username