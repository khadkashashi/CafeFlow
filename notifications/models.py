from django.conf import settings
from django.db import models


class Notification(models.Model):
    class Type(models.TextChoices):
        LOW_STOCK = "LOW_STOCK", "Low Stock"
        NEW_RESERVATION = "NEW_RESERVATION", "New Reservation"
        KITCHEN_READY = "KITCHEN_READY", "Kitchen Ready"
        PAYMENT_RECEIVED = "PAYMENT_RECEIVED", "Payment Received"
        NEW_ORDER = "NEW_ORDER", "New Order"
        TABLE_RESERVED = "TABLE_RESERVED", "Table Reserved"

    recipient = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="notifications")
    notification_type = models.CharField(max_length=30, choices=Type.choices)
    message = models.CharField(max_length=255)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"[{self.get_notification_type_display()}] {self.message}"

    def mark_read(self):
        self.is_read = True
        self.save(update_fields=["is_read"]) 