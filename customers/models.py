from django.conf import settings
from django.db import models


class Customer(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL,on_delete=models.SET_NULL,null=True,blank=True,related_name="customer_profile",help_text="Linked account if the customer registered online")
    name = models.CharField(max_length=150)
    phone = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)
    loyalty_points = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name

    @property
    def total_orders(self):
        return self.orders.count()

    def add_loyalty_points(self, amount_spent):
        """Rs.100 spent = 1 point, per your original plan."""
        points_earned = int(amount_spent // 100)
        self.loyalty_points += points_earned
        self.save(update_fields=["loyalty_points"])