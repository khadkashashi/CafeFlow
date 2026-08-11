from django.contrib import admin
from .models import Notification

# Register your models here.
@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ("recipient", "notification_type", "message", "is_read", "created_at")
    list_filter = ("notification_type", "is_read")
    list_editable = ("is_read",)