from django.contrib import admin
from .models import Invoice


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ("invoice_number", "order", "grand_total", "is_paid", "issued_at")
    list_filter = ("is_paid",)
    list_editable = ("is_paid",)
    readonly_fields = ("invoice_number", "subtotal", "discount", "tax", "grand_total", "issued_at")