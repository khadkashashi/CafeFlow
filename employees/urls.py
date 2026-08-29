from django.urls import path
from . import views
app_name = "employees"

urlpatterns = [
    path("", views.employee_list, name="employee_list"),
    path("add/", views.add_employee, name="add_employee"),
    path("<int:pk>/toggle/", views.toggle_active, name="toggle_active"),
    path("shift/", views.my_shift, name="my_shift"),
    path("shift/in/", views.clock_in, name="clock_in"),
    path("shift/out/", views.clock_out, name="clock_out"),
    path("shifts/", views.all_shifts, name="all_shifts"),
]