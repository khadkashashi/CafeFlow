from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from accounts.decorators import role_required
from accounts.models import User
from .forms import EmployeeForm
from .models import Employee,ShiftLog
from django.utils import timezone
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required


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


@login_required
def my_shift(request):
    employee = Employee.objects.filter(user=request.user).first()
    if not employee:
        return redirect("landing:home")  # not a staff member, nothing to show

    today_log = ShiftLog.objects.filter(employee=employee, date=timezone.now().date()).first()
    logs = ShiftLog.objects.filter(employee=employee).order_by("-date")[:10]
    return render(request, "employees/my_shift.html", {"employee": employee, "today_log": today_log, "logs": logs})


@login_required
@require_POST
def clock_in(request):
    employee = get_object_or_404(Employee, user=request.user)
    log, _ = ShiftLog.objects.get_or_create(employee=employee, date=timezone.now().date())
    if not log.clock_in:
        log.clock_in = timezone.now()
        log.save(update_fields=["clock_in"])
    return redirect("employees:my_shift")


@login_required
@require_POST
def clock_out(request):
    employee = get_object_or_404(Employee, user=request.user)
    log = ShiftLog.objects.filter(employee=employee, date=timezone.now().date()).first()
    if log and log.clock_in and not log.clock_out:
        log.clock_out = timezone.now()
        log.save(update_fields=["clock_out"])
    return redirect("employees:my_shift")


@role_required(User.Role.MANAGER)
def all_shifts(request):
    logs = ShiftLog.objects.select_related("employee__user").order_by("-date")[:100]
    return render(request, "employees/all_shifts.html", {"logs": logs})