from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    class Role(models.TextChoices):
        SUPER_ADMIN = "SUPER_ADMIN", "Super Admin"
        MANAGER = "MANAGER", "Manager"
        FRONT_DESK = "FRONT_DESK", "Front Desk"   
        WAITER = "WAITER", "Waiter"
        CHEF = "CHEF", "Chef"
        CUSTOMER = "CUSTOMER", "Customer"
    role = models.CharField(max_length=20, choices=Role.choices, default=Role.CUSTOMER)
    phone = models.CharField(max_length=20, blank=True)
    profile_picture = models.ImageField(upload_to="profiles/", blank=True, null=True)

    def __str__(self):
        return f"{self.username} ({self.role})"