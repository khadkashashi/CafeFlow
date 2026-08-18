from decimal import Decimal
from django.conf import settings
from django.db import models
from menu.models import FoodItem
from tables.models import Table


class Order(models.Model):
    class Status(models.TextChoices):
        DRAFT = "DRAFT", "Draft"
        PENDING = "PENDING", "Pending"
        PREPARING = "PREPARING", "Preparing"
        READY = "READY", "Ready"
        SERVED = "SERVED", "Served"
        COMPLETED = "COMPLETED", "Completed"
        CANCELLED = "CANCELLED", "Cancelled"

    class Source(models.TextChoices):
        DINE_IN = "DINE_IN", "Dine In"
        ONLINE = "ONLINE", "Online"
        PICKUP = "PICKUP", "Pickup"

    table = models.ForeignKey(Table, on_delete=models.SET_NULL, null=True, blank=True, related_name="orders")
    waiter = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="taken_orders")
    customer = models.ForeignKey("customers.Customer", on_delete=models.SET_NULL, null=True, blank=True, related_name="orders")
    source = models.CharField(max_length=20, choices=Source.choices, default=Source.DINE_IN)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.DRAFT)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("0.00"))
    discount = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("0.00"))
    tax = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("0.00"))
    grand_total = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("0.00"))
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        label = f"Table {self.table.table_number}" if self.table else self.get_source_display()
        return f"Order #{self.pk} — {label} ({self.get_status_display()})"

    def recalculate_totals(self, tax_rate: Decimal = Decimal("0.13")):
        """Recompute subtotal/tax/grand_total from current order items."""
        items_total = sum((item.line_total for item in self.items.all()), Decimal("0.00"))
        self.subtotal = items_total
        self.tax = (items_total - self.discount) * tax_rate
        self.grand_total = self.subtotal - self.discount + self.tax
        self.save(update_fields=["subtotal", "tax", "grand_total"])

    @classmethod
    def start_draft(cls, table, waiter=None, source=None):
        """Front desk clicks 'Start Order' on a table — creates the draft and occupies the table."""
        order = cls.objects.create(
            table=table, waiter=waiter, source=source or cls.Source.DINE_IN, status=cls.Status.DRAFT
        )
        if table:
            table.mark_occupied()
        return order

    def send_to_kitchen(self):
        """Explicitly push a draft order into the kitchen queue. Idempotent — safe to call more than once."""
        from kitchen.models import KitchenOrder

        if self.status == self.Status.DRAFT:
            self.status = self.Status.PENDING
            self.save(update_fields=["status"])
        KitchenOrder.objects.get_or_create(order=self)


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    food = models.ForeignKey(FoodItem, on_delete=models.PROTECT, related_name="order_items")
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=8, decimal_places=2, help_text="Price at time of order")
    note = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return f"{self.quantity} x {self.food.name} (Order #{self.order_id})"

    @property
    def line_total(self):
        if self.price is None:
            return Decimal("0.00")
        return self.price * self.quantity

    def save(self, *args, **kwargs):
        if not self.price:
            self.price = self.food.price
        super().save(*args, **kwargs)
        self.order.recalculate_totals()