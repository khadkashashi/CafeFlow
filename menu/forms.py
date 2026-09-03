from django import forms
from .models import Category, FoodItem

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ["name", "description", "image"]


class FoodItemForm(forms.ModelForm):
    class Meta:
        model = FoodItem
        fields = ["category", "name", "description", "price", "cost_price", "image", "preparation_time", "is_available", "stock", "calories"]