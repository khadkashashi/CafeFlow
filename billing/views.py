from django.shortcuts import render,get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from accounts.decorators import role_required
from accounts.models import User
from orders.models import Order
from .models import Invoice

# Create your views here.
@role_required( User.Role.FRONT_DESK, User.Role.MANAGER)
def generate_bill(request, order_pk):
    order = get_object_or_404(Order, pk=order_pk)
    invoice, created = Invoice.objects.get_or_create(order=order)
    return redirect("payments:payment_screen", invoice_pk=invoice.pk)

@login_required
def invoice_detail(request, pk):
    invoice = get_object_or_404(Invoice, pk=pk)
    return render(request, "billing/invoice_detail.html", {"invoice": invoice})

@login_required
def receipt(request, pk):
    invoice = get_object_or_404(Invoice, pk=pk)
    return render(request, "billing/receipt.html", {"invoice": invoice})

