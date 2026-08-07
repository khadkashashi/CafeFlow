from django.contrib import admin
from .models import Table
from django.core.files import File

# Register your models here.
@admin.register(Table)
class TableAdmin(admin.ModelAdmin):
    list_display = ("table_number", "capacity", "location", "status")
    list_filter = ("status", "location")
    list_editable = ("status",)
    ordering = ("table_number",)

    def save(self, *args, **kwargs):
        is_new = self._state.adding
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