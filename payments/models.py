from django.db import models
import uuid
from billing.models import Invoice
from django.conf import settings
# Create your models here.
class Payment(models.Model):
    class Method(models.TextChoices):
        CASH = "CASH", "Cash"
        CARD = "CARD", "Card"
        ESEWA = "ESEWA", "eSewa"
        KHALTI = "KHALTI", "Khalti"
        FONEPAY = "FONEPAY", "FonePay"
    class Status(models.TextChoices):
            PENDING = "PENDING", "Pending"
            SUCCESS = "SUCCESS", "Success"
            FAILED = "FAILED", "Failed"

    invoice= models.ForeignKey(Invoice,on_delete=models.CASCADE, related_name="payments")
    payment_method= models.CharField(max_length=20,choices=Method.choices, default=Method.KHALTI)
    amount= models.DecimalField(max_digits=10, decimal_places=2)
    pidx = models.CharField(max_length=100, blank=True, null=True)
    transaction_id=models.CharField(max_length=100, blank=True, unique= True, null=True)
    status=models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    paid_at= models.DateTimeField(null=True, blank=True)


    class Meta:
         ordering=["-paid_at"]

    def __str__(self):
         return f"{self.get_payment_method_display()}- Rs.{self.amount} ({self.get_status_display()})"
    def save(self, *args, **kwargs):
        from django.utils import timezone

        if not self.transaction_id:
            self.transaction_id = f"TXN-{uuid.uuid4().hex[:10].upper()}"

        if self.status == self.Status.SUCCESS and not self.paid_at:
            self.paid_at = timezone.now()

        super().save(*args, **kwargs)
        self.invoice.check_fully_paid()


class InvoicePaymentMixin:
    """Mixin placeholder — actual method lives on Invoice, see billing/models.py update below."""

class CashClosing(models.Model):
    date = models.DateField(unique=True)
    expected_cash = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    counted_cash = models.DecimalField(max_digits=10, decimal_places=2)
    notes = models.CharField(max_length=255, blank=True)
    closed_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    closed_at = models.DateTimeField(auto_now_add=True)

    @property
    def difference(self):
        return self.counted_cash - self.expected_cash

    def __str__(self):
        return f"Cash closing {self.date} — diff Rs.{self.difference}"


