from django.db import models
from menu.models import FoodItem

class Supplier(models.Model):
    name = models.CharField(max_length=150)
    phone = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)
    address = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    class Unit(models.TextChoices):
        GRAM = "G", "Gram"
        KILOGRAM = "KG", "Kilogram"
        MILLILITER = "ML", "Milliliter"
        LITER = "L", "Liter"
        PIECE = "PC", "Piece"

    name = models.CharField(max_length=150, unique=True)
    unit = models.CharField(max_length=5, choices=Unit.choices, default=Unit.PIECE)
    quantity = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    minimum_stock = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    supplier = models.ForeignKey(Supplier, on_delete=models.SET_NULL, null=True, blank=True)
    cost = models.DecimalField(max_digits=10, decimal_places=2, default=0, help_text="Cost per unit")

    def __str__(self):
        return f"{self.name} ({self.quantity} {self.unit})"

    @property
    def is_low_stock(self):
        return self.quantity <= self.minimum_stock


class Recipe(models.Model):
    """Links a FoodItem to the ingredients (and quantities) it consumes when sold."""
    food = models.ForeignKey(FoodItem, on_delete=models.CASCADE, related_name="recipe_items")
    ingredient = models.ForeignKey(Ingredient, on_delete=models.PROTECT)
    quantity_required = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        unique_together = ("food", "ingredient")

    def __str__(self):
        return f"{self.food.name} needs {self.quantity_required} {self.ingredient.unit} of {self.ingredient.name}"


class Purchase(models.Model):
    supplier = models.ForeignKey(Supplier, on_delete=models.SET_NULL, null=True)
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE, related_name="purchases")
    quantity = models.DecimalField(max_digits=10, decimal_places=2)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.quantity} {self.ingredient.unit} of {self.ingredient.name} from {self.supplier}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.ingredient.quantity += self.quantity
        self.ingredient.save(update_fields=["quantity"])