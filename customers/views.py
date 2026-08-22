from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from orders.models import Order
from .models import Customer


@login_required
def my_account(request):
    customer, _ = Customer.objects.get_or_create(user=request.user,
        defaults={
            "name": request.user.get_full_name() or request.user.username,
            "phone": request.user.phone,
            "email": request.user.email,
        },
    )
    orders = Order.objects.filter(customer=customer).order_by("-created_at")[:10]
    points_value = customer.loyalty_points * settings.LOYALTY_POINT_VALUE
    context={
        "customer": customer, 
        "orders": orders, 
        "points_value": points_value
    }

    return render(request,"customers/my_account.html",context)