from django.urls import path
from . import views
app_name = "employees"

urlpatterns = [
    path("", views.employee_list, name="employee_list"),
    path("add/", views.add_employee, name="add_employee"),
    path("<int:pk>/toggle/", views.toggle_active, name="toggle_active"),
]