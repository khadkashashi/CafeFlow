from django.shortcuts import render
from accounts.decorators import role_required
from accounts.models import User
from billing.models import Invoice
from orders.models import Order
from .models import Table

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
