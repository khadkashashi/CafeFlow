from django import forms
from accounts.models import User
from .models import Employee


class EmployeeForm(forms.ModelForm):
    username = forms.CharField(max_length=150)
    password = forms.CharField(widget=forms.PasswordInput, required=False, help_text="Leave blank when editing to keep current password")

    class Meta:
        model = Employee
        fields = ["position", "salary", "joining_date", "shift"]
        widgets = {"joining_date": forms.DateInput(attrs={"type": "date"})}