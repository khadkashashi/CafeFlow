from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from accounts.decorators import role_required
from accounts.models import User
from orders.models import Order
from .models import Customer


@role_required(User.Role.CUSTOMER)
def my_account(request):
    customer, _ = Customer.objects.get_or_create(user=request.user,
        defaults={
            "name": request.user.get_full_name() or request.user.username,
            "phone": request.user.phone,
            "email": request.user.email,
        },
    )
    orders = Order.objects.filter(customer=customer).order_by("-created_at")[:10]
    from django.conf import settings
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