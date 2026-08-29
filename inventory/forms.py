from django import forms
from .models import Ingredient, Purchase, Supplier
from django.forms import inlineformset_factory
from menu.models import FoodItem
from .models import Recipe

RecipeFormSet = inlineformset_factory(FoodItem, Recipe, fields=["ingredient", "quantity_required"], extra=3, can_delete=True)

class IngredientForm(forms.ModelForm):
    class Meta:
        model = Ingredient
        fields = ["name", "unit", "quantity", "minimum_stock", "supplier", "cost"]

class PurchaseForm(forms.ModelForm):
    class Meta:
        model = Purchase
        fields = ["ingredient", "supplier", "quantity", "price"]


class SupplierForm(forms.ModelForm):
    class Meta:
        model = Supplier
        fields = ["name", "phone", "email", "address"]