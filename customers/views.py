from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from accounts.decorators import role_required
from accounts.models import User
from orders.models import Order
from .models import Customer
from django.conf import settings
from django.contrib import messages

@role_required(User.Role.CUSTOMER)
def my_account(request):
    customer, _ = Customer.objects.get_or_create(user=request.user,
        defaults={
            "name": request.user.get_full_name() or request.user.username,
            "phone": None,
            "email": request.user.email,
        },
    )
    if request.method == "POST":
        phone = request.POST.get("phone")
        if Customer.objects.filter(phone=phone).exclude(pk=customer.pk).exists():
            messages.error(request, "This phone number is already associated with another account.")
        else:
            customer.phone = phone
            customer.save()
            messages.success(request, "Account updated successfully!")
            return redirect("customers:my_account")
    orders = Order.objects.filter(customer=customer).order_by("-created_at")[:10]
    points_value = customer.loyalty_points * settings.LOYALTY_POINT_VALUE
    return render(request, "customers/my_account.html", {"customer": customer, "orders": orders, "points_value": points_value})


def check_points(request):
    """Public lookup for walk-in customers who have no login — check points by phone."""
    customer = None
    searched = False
    if request.method == "POST":
        phone = request.POST.get("phone", "").strip()
        searched = True
        customer = Customer.objects.filter(phone=phone).first()

    return render(request, "customers/check_points.html", {"customer": customer, "searched": searched})