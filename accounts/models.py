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
    email = models.EmailField(unique=True, blank=True, null=True)
    profile_picture = models.ImageField(upload_to="profiles/", blank=True, null=True)

    def __str__(self):
        return f"{self.username} ({self.role})"

    @property
    def can_access_pos(self):
        return self.is_superuser or self.role in (self.Role.WAITER, self.Role.FRONT_DESK, self.Role.MANAGER)

    @property
    def can_access_kitchen(self):
        return self.is_superuser or self.role in (self.Role.CHEF, self.Role.MANAGER)

    @property
    def can_access_reception(self):
        return self.is_superuser or self.role in (self.Role.FRONT_DESK, self.Role.MANAGER)

    @property
    def can_access_reports(self):
        return self.is_superuser or self.role == self.Role.MANAGER

    @property
    def can_manage_orders(self):
        """Can start orders, add/remove items, send to kitchen —> the waiter's job."""
        return self.is_superuser or self.role in (self.Role.WAITER, self.Role.MANAGER)

    @property
    def can_bill(self):
        """Can view billing, apply discounts, generate bills, take payment —> front desk's job."""
        return self.is_superuser or self.role in (self.Role.FRONT_DESK, self.Role.MANAGER)


    @property
    def can_manage_staff(self):
        return self.is_superuser or self.role == self.Role.MANAGER

    @property
    def can_manage_inventory(self):
        return self.is_superuser or self.role == self.Role.MANAGER

    @property
    def can_view_inventory(self):
        return self.is_superuser or self.role in (self.Role.CHEF, self.Role.MANAGER)

    @property
    def is_staff_member(self):
         return self.is_superuser or self.role != self.Role.CUSTOMER