from django.db import models
from django.conf import settings


# Create your models here.
class Employee(models.Model):
    class Shift(models.TextChoices):
        MORNING = "MORNING", "Morning"
        AFTERNOON = "AFTERNOON", "Afternoon"
        EVENING = "EVENING", "Evening"
        NIGHT = "NIGHT", "Night"

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="employee_profile"
    )
    position = models.CharField(max_length=100, help_text="e.g. Head Chef, Waiter, Manager")
    salary = models.DecimalField(max_digits=10, decimal_places=2)
    joining_date = models.DateField()
    shift = models.CharField(max_length=20, choices=Shift.choices, default=Shift.MORNING)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["user__username"]

    def __str__(self):
        return f"{self.user.get_full_name() or self.user.username} — {self.position}"