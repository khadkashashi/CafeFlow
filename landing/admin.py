from django.contrib import admin
from .models import Review

# Register your models here.
@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ("customer", "order", "rating", "created_at")
    list_filter = ("rating",)