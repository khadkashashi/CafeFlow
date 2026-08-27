from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST
from menu.models import FoodItem
from orders.models import Order, OrderItem
from .cart import Cart
from customers.models import Customer
from tables.models import Table


def cart_detail(request):
    cart = Cart(request)
    return render(request, "cart/cart_detail.html", {"cart": cart})


@require_POST #-->@require_POST on add/remove — same principle as the kitchen buttons earlier: changing data should never happen via a plain GET link.
def cart_add(request, food_id):
    cart = Cart(request)
    food = get_object_or_404(FoodItem, id=food_id, is_available=True)
    quantity = int(request.POST.get("quantity", 1))
    cart.add(food.id, quantity)
    return redirect("cart:cart_detail")


@require_POST
def cart_remove(request, food_id):
    cart = Cart(request)
    cart.remove(food_id)
    return redirect("cart:cart_detail")


@login_required
def checkout(request):
    cart = Cart(request)
    if len(cart) == 0:
        return redirect("cart:cart_detail")
    customer, _ = Customer.objects.get_or_create(user=request.user,
        defaults={
            "name": request.user.get_full_name() or request.user.username,
            "phone": request.user.phone,
            "email": request.user.email,
        },
    )
    table_id = request.session.pop("dine_in_table_id", None)
    table = Table.objects.filter(pk=table_id).first() if table_id else None
    order = Order.objects.create(customer=customer,         
    source=Order.Source.DINE_IN if table else Order.Source.ONLINE, status=Order.Status.PENDING)
    for item in cart:
        OrderItem.objects.create(order=order, food=item["food"], quantity=item["quantity"])
    order.recalculate_totals()
    order.send_to_kitchen()
    if table and table.status == Table.Status.AVAILABLE:
        table.mark_occupied()
    cart.clear()
    return redirect("orders:order_detail", pk=order.pk)