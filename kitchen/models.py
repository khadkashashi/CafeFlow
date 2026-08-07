from django.conf import settings
from django.db import models
from orders.models import Order
from django.utils import timezone


class KitchenOrder(models.Model):
    class Status(models.TextChoices):
        QUEUED = "QUEUED", "Queued"
        IN_PROGRESS = "IN_PROGRESS", "In Progress"
        DONE = "DONE", "Done"

    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name="kitchen_ticket")
    chef = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.SET_NULL,null=True,blank=True,related_name="kitchen_orders")
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.QUEUED)
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["order__created_at"]

    def __str__(self):
        return f"Kitchen ticket for Order #{self.order_id} ({self.get_status_display()})"

    def start(self, chef=None):
        self.status = self.Status.IN_PROGRESS
        self.started_at = timezone.now()
        if chef:
            self.chef = chef
        self.save(update_fields=["status", "started_at", "chef"])
        self.order.status = Order.Status.PREPARING
        self.order.save(update_fields=["status"])

    def complete(self):
        self.status = self.Status.DONE
        self.completed_at = timezone.now()
        self.save(update_fields=["status", "completed_at"])
        self.order.status = Order.Status.READY
        self.order.save(update_fields=["status"])