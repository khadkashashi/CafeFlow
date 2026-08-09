from django import forms
from django.forms import inlineformset_factory
from .models import Order,OrderItem

class OrderForm(forms.ModelForm):
    class Meta:
        model= Order
        fields=["table", "source"]

OrderItemFormSet= inlineformset_factory(Order,OrderItem, fields=["food","quantity","note"],extra=3,can_delete=True)
#inlineformset_factory gives us a formset pre-wired to the Order FK — this is Django's built-in tool for exactly this "one parent, many children, one submit" pattern, so we don't need custom JS-driven cart logic yet.