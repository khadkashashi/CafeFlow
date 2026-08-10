from django.contrib import admin
from .models import Customer

# Register your models here.
@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ("name", "phone", "email", "loyalty_points", "total_orders")
    search_fields = ("name", "phone", "email")