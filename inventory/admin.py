from django.contrib import admin
from .models import Ingredient, Purchase, Recipe, Supplier

@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = ("name", "phone", "email")


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ("name", "quantity", "unit", "minimum_stock", "is_low_stock", "supplier")
    list_filter = ("supplier",)

    def is_low_stock(self, obj):
        return obj.is_low_stock
    is_low_stock.boolean = True


class RecipeInline(admin.TabularInline):
    model = Recipe
    extra = 1


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ("food", "ingredient", "quantity_required")


@admin.register(Purchase)
class PurchaseAdmin(admin.ModelAdmin):
    list_display = ("ingredient", "supplier", "quantity", "price", "date")