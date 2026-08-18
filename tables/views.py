from django.shortcuts import render,get_object_or_404, redirect
from django.views.decorators.http import require_POST
from accounts.decorators import role_required
from accounts.models import User
from billing.models import Invoice
from orders.models import Order,OrderItem
from .models import Table
from menu.models import FoodItem

# Create your views here.

@role_required(User.Role.FRONT_DESK, User.Role.MANAGER)
def reception_dashboard(request):
    all_tables = Table.objects.all()
    recent_orders = Order.objects.exclude(status__in=[Order.Status.COMPLETED, Order.Status.CANCELLED]).select_related("table")[:10]
    pending_bills = Invoice.objects.filter(is_paid=False).select_related("order")
    context={
    "tables": all_tables,
    "recent_orders": recent_orders,
    "pending_bills": pending_bills,
    }
    return render(request,"tables/reception_dashboard.html",context)

ACTIVE_STATUSES_EXCLUDE = [Order.Status.COMPLETED, Order.Status.CANCELLED]
@role_required(User.Role.WAITER, User.Role.FRONT_DESK, User.Role.MANAGER)
def table_detail(request, pk):
    table = get_object_or_404(Table, pk=pk)
    order = (Order.objects.filter(table=table).exclude(status__in=ACTIVE_STATUSES_EXCLUDE).order_by("-created_at").first())
    food_items = FoodItem.objects.filter(is_available=True).select_related("category")
    context={
        "table": table, 
        "order": order, 
        "food_items": food_items
    }
    return render(request,"tables/table_detail.html",context)


@role_required(User.Role.WAITER, User.Role.FRONT_DESK, User.Role.MANAGER)
@require_POST
def start_order(request, pk):
    table = get_object_or_404(Table, pk=pk)
    has_active = Order.objects.filter(table=table).exclude(status__in=ACTIVE_STATUSES_EXCLUDE).exists()
    if not has_active:
        Order.start_draft(table=table, waiter=request.user)
    return redirect("tables:table_detail", pk=table.pk)


@role_required(User.Role.WAITER, User.Role.FRONT_DESK, User.Role.MANAGER)
@require_POST
def add_item_to_order(request, pk):
    order = get_object_or_404(Order, pk=pk)
    food = get_object_or_404(FoodItem, pk=request.POST.get("food_id"))
    quantity = int(request.POST.get("quantity", 1))
    item, created = OrderItem.objects.get_or_create(order=order, food=food, defaults={"quantity": quantity, "price": food.price})
    if not created:
        item.quantity += quantity
        item.save()
    return redirect("tables:table_detail", pk=order.table.pk)


@role_required(User.Role.WAITER, User.Role.FRONT_DESK, User.Role.MANAGER)
@require_POST
def send_order_to_kitchen(request, pk):
    order = get_object_or_404(Order, pk=pk)
    order.send_to_kitchen()
    return redirect("tables:table_detail", pk=order.table.pk)