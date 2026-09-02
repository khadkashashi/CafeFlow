from django.db import models
from customers.models import Customer
from tables.models import Table

class Reservation(models.Model):
    class Status(models.TextChoices):
        PENDING = "PENDING", "Pending"
        CONFIRMED = "CONFIRMED", "Confirmed"
        CANCELLED = "CANCELLED", "Cancelled"
        COMPLETED = "COMPLETED", "Completed"

    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name="reservations")
    table = models.ForeignKey(Table, on_delete=models.SET_NULL, null=True, blank=True, related_name="reservations")
    date = models.DateField()
    time = models.TimeField()
    guest_count = models.PositiveIntegerField(default=1)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["date", "time"]

    def __str__(self):
        return f"{self.customer.name} — {self.date} {self.time} ({self.get_status_display()})"

    def confirm(self):
        self.status = self.Status.CONFIRMED
        self.save(update_fields=["status"])
        if self.table:
            self.table.status = Table.Status.RESERVED
            self.table.save(update_fields=["status"])

    def cancel(self):
        self.status = self.Status.CANCELLED
        self.save(update_fields=["status"])
        if self.table and self.table.status == Table.Status.RESERVED:
            self.table.mark_available()

    def complete(self):
        self.status = self.Status.COMPLETED
        self.save(update_fields=["status"])