from django.db import models
from django.conf import settings
from django.utils import timezone


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


class ShiftLog(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name="shift_logs")
    date = models.DateField(default=timezone.now)
    clock_in = models.DateTimeField(null=True, blank=True)
    clock_out = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-date"]

    def __str__(self):
        return f"{self.employee} — {self.date}"

    @property
    def hours_worked(self):
        if self.clock_in and self.clock_out:
            return round((self.clock_out - self.clock_in).total_seconds() / 3600, 2)
        return None