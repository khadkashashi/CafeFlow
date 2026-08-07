from django.contrib import admin
from .models import Order, OrderItem


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 1
    readonly_fields = ("line_total",)
    
    def line_total(self, obj):
        return obj.line_total


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "table",
        "source",
        "status",
        "grand_total",
        "created_at",
    )
    list_filter = ("status", "source")
    list_editable = ("status",)
    inlines = [OrderItemInline]
    readonly_fields = ("subtotal", "tax", "grand_total", "created_at", "updated_at")