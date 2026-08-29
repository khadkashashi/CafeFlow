from django.shortcuts import render,get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from accounts.decorators import role_required
from accounts.models import User
from orders.models import Order
from .models import Invoice
from customers.models import Customer
from django.views.decorators.http import require_POST

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

@role_required(User.Role.FRONT_DESK, User.Role.MANAGER)
def order_bill(request, order_pk):
    order = get_object_or_404(Order, pk=order_pk)
    invoice = Invoice.objects.filter(order=order).first()
    return render(request, "billing/order_bill.html", {"order": order, "invoice": invoice})

@role_required(User.Role.FRONT_DESK, User.Role.MANAGER)
@require_POST
def link_customer(request, order_pk):
    order = get_object_or_404(Order, pk=order_pk)
    phone = request.POST.get("phone", "").strip()
    name = request.POST.get("name", "").strip()
    if phone and name:
        customer = Customer.objects.filter(phone=phone).order_by("id").first()
        if not customer:
            customer = Customer.objects.create(phone=phone, name=name)
        order.customer = customer
        order.save(update_fields=["customer"])
    return redirect("billing:order_bill", order_pk=order.pk)