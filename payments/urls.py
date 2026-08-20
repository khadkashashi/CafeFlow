from django.urls import path
from . import views
app_name = "payments"

urlpatterns = [
    path("invoice/<int:invoice_pk>/pay/", views.payment_screen, name="payment_screen"),
]