import uuid
from django.db import models
from orders.models import Order


class Invoice(models.Model):
    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name="invoice")
    invoice_number = models.CharField(max_length=20, unique=True, editable=False, blank=True)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    discount = models.DecimalField(max_digits=10, decimal_places=2)
    tax = models.DecimalField(max_digits=10, decimal_places=2)
    grand_total = models.DecimalField(max_digits=10, decimal_places=2)
    is_paid = models.BooleanField(default=False)
    issued_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-issued_at"]

    def __str__(self):
        return f"Invoice {self.invoice_number} — Order #{self.order_id}"

    def save(self, *args, **kwargs):
        if not self.invoice_number:
            self.invoice_number = f"INV-{uuid.uuid4().hex[:8].upper()}"
        # Snapshot totals from the order at billing time
        if not self.pk:
            self.subtotal = self.order.subtotal
            self.discount = self.order.discount
            self.tax = self.order.tax
            self.grand_total = self.order.grand_total
        super().save(*args, **kwargs)

def check_fully_paid(self):
    total_paid = sum((p.amount for p in self.payments.filter(status="SUCCESS")),self.grand_total.__class__("0.00"))
    if total_paid >= self.grand_total and not self.is_paid:
        self.is_paid = True
        self.save(update_fields=["is_paid"])
        self.order.status = self.order.Status.COMPLETED
        self.order.save(update_fields=["status"])