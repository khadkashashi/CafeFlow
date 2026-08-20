from django.urls import path
from . import views
app_name = "billing"

urlpatterns = [
    path("order/<int:order_pk>/generate/", views.generate_bill, name="generate_bill"),
    path("invoice/<int:pk>/", views.invoice_detail, name="invoice_detail"),
    path("invoice/<int:pk>/receipt/", views.receipt, name="receipt"),
]