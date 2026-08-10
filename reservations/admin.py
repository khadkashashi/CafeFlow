from django.contrib import admin
from .models import Reservation

@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    list_display = ("customer", "table", "date", "time", "guest_count", "status")
    list_filter = ("status", "date")
    list_editable = ("status",)
    date_hierarchy = "date"

#date_hierarchy gives you a nice drill-down-by-date navigation bar in admin — small polish, worth knowing it exists.