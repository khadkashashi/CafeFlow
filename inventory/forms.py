from django import forms
from .models import Ingredient, Purchase

class IngredientForm(forms.ModelForm):
    class Meta:
        model = Ingredient
        fields = ["name", "unit", "quantity", "minimum_stock", "supplier", "cost"]

class PurchaseForm(forms.ModelForm):
    class Meta:
        model = Purchase
        fields = ["ingredient", "supplier", "quantity", "price"]