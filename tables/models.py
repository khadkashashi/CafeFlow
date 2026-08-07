from io import BytesIO

import qrcode
from django.core.files import File
from django.db import models


class Table(models.Model):
    class Status(models.TextChoices):
        AVAILABLE = "AVAILABLE", "Available"
        OCCUPIED = "OCCUPIED", "Occupied"
        RESERVED = "RESERVED", "Reserved"
        CLEANING = "CLEANING", "Cleaning"

    table_number = models.PositiveIntegerField(unique=True)
    capacity = models.PositiveIntegerField(default=2)
    location = models.CharField(max_length=100, blank=True, help_text="e.g. Indoor, Patio, 2nd Floor")
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.AVAILABLE)
    qr_code = models.ImageField(upload_to="table_qr/", blank=True, null=True)

    class Meta:
        ordering = ["table_number"]

    def __str__(self):
        return f"Table {self.table_number} ({self.get_status_display()})"

    def mark_occupied(self):
        self.status = self.Status.OCCUPIED
        self.save(update_fields=["status"])

    def mark_available(self):
        self.status = self.Status.AVAILABLE
        self.save(update_fields=["status"])

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if not self.qr_code:
            self.generate_qr()

    def generate_qr(self):
        qr = qrcode.make(f"table-{self.table_number}")
        buffer = BytesIO()
        qr.save(buffer, format="PNG")
        filename = f"table_{self.table_number}_qr.png"
        self.qr_code.save(filename, File(buffer), save=False)
        super().save(update_fields=["qr_code"])