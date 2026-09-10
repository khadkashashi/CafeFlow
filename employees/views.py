from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from accounts.decorators import role_required
from accounts.models import User
from .forms import EmployeeForm
from .models import Employee,ShiftLog
from django.utils import timezone
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from datetime import date as date_cls, timedelta

@role_required(User.Role.MANAGER)
def employee_list(request):
    status_filter = request.GET.get("status", "active")
    position_filter = request.GET.get("position", "")
    employees = Employee.objects.select_related("user").all()
    if status_filter == "active":
        employees = employees.filter(is_active=True)
    elif status_filter == "inactive":
        employees = employees.filter(is_active=False)
    # status_filter == "all" → no filtering
    if position_filter:
        employees = employees.filter(position__iexact=position_filter)
    positions = Employee.objects.values_list("position", flat=True).distinct().order_by("position")
    context={
            "employees": employees,
            "status_filter": status_filter,
            "position_filter": position_filter, 
            "positions": positions
    }
    return render(request, "employees/employee_list.html",context)


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
    if request.user.role == request.user.Role.CUSTOMER:
        return redirect("landing:home")

    employee, _ = Employee.objects.get_or_create(
        user=request.user,
        defaults={
            "position": request.user.get_role_display(),
            "salary": 0,
            "joining_date": timezone.now().date(),
            "shift": Employee.Shift.MORNING,
        },
    )

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
    filter_choice = request.GET.get("range", "today")
    include_inactive = request.GET.get("include_inactive") == "1"
    today = timezone.now().date()
    logs = ShiftLog.objects.select_related("employee__user")
    if not include_inactive:
        logs = logs.filter(employee__is_active=True)

    if filter_choice == "today":
        logs = logs.filter(date=today)
    elif filter_choice == "yesterday":
        logs = logs.filter(date=today - timedelta(days=1))
    elif filter_choice == "week":
        logs = logs.filter(date__gte=today - timedelta(days=7))
    elif filter_choice == "custom":
        custom_date = request.GET.get("date")
        if custom_date:
            logs = logs.filter(date=custom_date)
    logs = logs.order_by("-date", "employee__user__username")[:200]
    context={
        "logs": logs,
        "filter_choice": filter_choice,
        "custom_date": request.GET.get("date", ""),
        "include_inactive": include_inactive,
    }

    return render(request, "employees/all_shifts.html", context)

@role_required(User.Role.MANAGER)
def attendance_today(request):
    filter_choice = request.GET.get("range", "today")
    today = timezone.now().date()

    if filter_choice in ("week", "all"):
        employees = Employee.objects.filter(is_active=True).select_related("user")
        logs = ShiftLog.objects.all()
        if filter_choice == "week":
            logs = logs.filter(date__gte=today - timedelta(days=7))

        summary = []
        for emp in employees:
            emp_logs = logs.filter(employee=emp)
            days_worked = emp_logs.filter(clock_in__isnull=False).count()
            total_hours = sum((l.hours_worked or 0) for l in emp_logs)
            summary.append({"employee": emp, "days_worked": days_worked, "total_hours": round(total_hours, 2)})

        return render(request, "employees/attendance_summary.html", {"summary": summary, "filter_choice": filter_choice})

    # single-day view (today / yesterday / custom)
    if filter_choice == "yesterday":
        target_date = today - timedelta(days=1)
    elif filter_choice == "custom":
        custom_date = request.GET.get("date")
        target_date = date_cls.fromisoformat(custom_date) if custom_date else today
    else:
        target_date = today

    employees = Employee.objects.filter(is_active=True).select_related("user")
    logs_for_date = {log.employee_id: log for log in ShiftLog.objects.filter(date=target_date)}
    present, completed, absent = [], [], []
    for emp in employees:
        log = logs_for_date.get(emp.id)
        if not log or not log.clock_in:
            absent.append(emp)
        elif log.clock_in and not log.clock_out:
            present.append((emp, log))
        else:
            completed.append((emp, log))
    context={
        "present": present, 
        "completed": completed,
        "absent": absent,
        "target_date": target_date, 
        "filter_choice": filter_choice,
        "custom_date": request.GET.get("date", ""),
    }

    return render(request, "employees/attendance_today.html", context)