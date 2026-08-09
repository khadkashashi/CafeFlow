from django.contrib import admin
from .models import Payment
# Register your models here.

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
       list_display = ("transaction_id", "invoice", "payment_method", "amount", "status", "paid_at")
       list_filter = ("payment_method", "status")
       list_editable = ("status",)
       readonly_fields = ("transaction_id", "paid_at")
