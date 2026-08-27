from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from accounts.decorators import role_required
from accounts.models import User
from .forms import EmployeeForm
from .models import Employee


@role_required(User.Role.MANAGER)
def employee_list(request):
    employees = Employee.objects.select_related("user").all()
    return render(request, "employees/employee_list.html", {"employees": employees})


@role_required(User.Role.MANAGER)
def add_employee(request):
    if request.method == "POST":
        form = EmployeeForm(request.POST)
        role = request.POST.get("role")
        if form.is_valid() and role in dict(User.Role.choices):
            username = form.cleaned_data["username"]
            password = form.cleaned_data["password"] or User.objects.make_random_password()

            if User.objects.filter(username=username).exists():
                messages.error(request, f"Username '{username}' already exists.")
            else:
                user = User.objects.create_user(username=username, password=password, role=role)
                employee = form.save(commit=False)
                employee.user = user
                employee.save()
                messages.success(request, f"Created {username} — temporary password: {password}")
                return redirect("employees:employee_list")
    else:
        form = EmployeeForm()

    return render(request, "employees/employee_form.html", {"form": form, "roles": User.Role.choices})


@role_required(User.Role.MANAGER)
def toggle_active(request, pk):
    employee = get_object_or_404(Employee, pk=pk)
    employee.is_active = not employee.is_active
    employee.save(update_fields=["is_active"])
    return redirect("employees:employee_list")