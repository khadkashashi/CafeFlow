from django import forms
from orders.models import Order

class CheckoutForm(forms.Form):
    contact_name = forms.CharField(max_length=150, label="Full Name")
    contact_phone = forms.CharField(max_length=20, label="Phone Number")
    delivery_option = forms.ChoiceField(choices=Order.DeliveryOption.choices, widget=forms.RadioSelect)
    delivery_address = forms.CharField(widget=forms.Textarea(attrs={"rows": 2}), required=False, label="Delivery Address")
    payment_method = forms.ChoiceField(choices=[("COD", "Cash on Delivery/Pickup"), ("KHALTI", "Khalti")])

    def clean(self):
        cleaned = super().clean()
        if cleaned.get("delivery_option") == "DELIVERY" and not cleaned.get("delivery_address"):
            self.add_error("delivery_address", "Address is required for delivery.")
        return cleaned

    """The clean() override enforces a real business rule at the form level: you can't pick delivery without giving an address"""