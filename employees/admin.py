from django.contrib import admin
from .models import Employee

# Register your models here.
@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ("user", "position", "shift", "salary", "joining_date", "is_active")
    list_filter = ("shift", "is_active", "position")
    list_editable = ("is_active",)
    search_fields = ("user__username", "position")