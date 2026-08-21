from django.shortcuts import render,get_object_or_404, redirect
from django.views.decorators.http import require_POST
from accounts.decorators import role_required
from accounts.models import User
from billing.models import Invoice
from orders.models import Order,OrderItem
from .models import Table
from menu.models import FoodItem
from decimal import Decimal, InvalidOperation
# Create your views here.

@role_required(User.Role.FRONT_DESK, User.Role.MANAGER)
def reception_dashboard(request):
    active_orders = Order.objects.filter(table__isnull=True).exclude(status__in=[Order.Status.COMPLETED, Order.Status.CANCELLED, Order.Status.DRAFT]).select_related("customer").order_by("-created_at")
    pending_bills = Invoice.objects.filter(is_paid=False).select_related("order")
    all_tables = Table.objects.all()
    context={
        "active_orders": active_orders, 
        "pending_bills": pending_bills, 
        "tables": all_tables
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

@role_required(User.Role.WAITER, User.Role.FRONT_DESK, User.Role.MANAGER)
@require_POST
def mark_table_clean(request, pk):
    table = get_object_or_404(Table, pk=pk)
    if table.status == Table.Status.CLEANING:
        table.mark_available()
    return redirect("tables:reception_dashboard")


@role_required(User.Role.WAITER, User.Role.FRONT_DESK, User.Role.MANAGER)
@require_POST
def remove_item_from_order(request, item_pk):
    item = get_object_or_404(OrderItem, pk=item_pk)
    table_pk = item.order.table.pk
    if item.order.status == Order.Status.DRAFT:
        item.delete()
        item.order.recalculate_totals()

    return redirect("tables:table_detail", pk=table_pk)


@role_required(User.Role.WAITER, User.Role.FRONT_DESK, User.Role.MANAGER)
@require_POST
def update_item_quantity(request, item_pk):
    item = get_object_or_404(OrderItem, pk=item_pk)
    table_pk = item.order.table.pk
    if item.order.status == Order.Status.DRAFT:
        quantity = int(request.POST.get("quantity", item.quantity))
        if quantity < 1:
            item.delete()
            item.order.recalculate_totals()
        else:
            item.quantity = quantity
            item.save()

    return redirect("tables:table_detail", pk=table_pk)

@role_required(User.Role.FRONT_DESK, User.Role.MANAGER)
@require_POST
def apply_discount(request, pk):
    order = get_object_or_404(Order, pk=pk)
    if order.status not in (Order.Status.COMPLETED, Order.Status.CANCELLED):
        try:
            discount = Decimal(request.POST.get("discount", "0"))
        except InvalidOperation:
            discount = Decimal("0.00")
        if discount < 0:
            discount = Decimal("0.00")
        order.discount = discount
        order.save(update_fields=["discount"])
        order.recalculate_totals()

    return redirect("billing:order_bill", order_pk=order.pk)
@role_required(User.Role.WAITER, User.Role.MANAGER)
def waiter_tables(request):
    tables = Table.objects.all()
    return render(request, "tables/waiter_tables.html", {"tables": tables})


@role_required(User.Role.FRONT_DESK, User.Role.MANAGER)
def table_bill(request, pk):
    table = get_object_or_404(Table, pk=pk)
    order = (Order.objects.filter(table=table) .exclude(status__in=[Order.Status.DRAFT, Order.Status.COMPLETED, Order.Status.CANCELLED]) .order_by("-created_at").first())
    if not order:
        return redirect("tables:reception_dashboard")
    return redirect("billing:order_bill", order_pk=order.pk)