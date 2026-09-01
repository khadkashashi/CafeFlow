from datetime import timedelta
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Sum, F
from django.utils import timezone
from django.shortcuts import render
from accounts.decorators import role_required
from accounts.models import User
from inventory.models import Ingredient
from orders.models import Order, OrderItem
from payments.models import Payment

# Create your views here.
@role_required(User.Role.MANAGER)
def reports_dashboard(request):
    today = timezone.now().date()
    last_7_days = today - timedelta(days=7)
    todays_revenue = (Order.objects.filter(created_at__date=today, status=Order.Status.COMPLETED).aggregate(total=Sum("grand_total"))["total"] or 0)
    weekly_revenue = (Order.objects.filter(created_at__date__gte=last_7_days, status=Order.Status.COMPLETED).aggregate(total=Sum("grand_total"))["total"] or 0)
    best_selling = (OrderItem.objects.values("food__name").annotate(total_sold=Sum("quantity")).order_by("-total_sold")[:5])
    low_stock_items = Ingredient.objects.filter(quantity__lte=F("minimum_stock"))
    order_count_today = Order.objects.filter(created_at__date=today).count()
    payment_breakdown = (Payment.objects.filter(status=Payment.Status.SUCCESS).values("payment_method").annotate(total=Sum("amount"), count=Count("id")).order_by("-total"))
    context={
        "todays_revenue": todays_revenue,
        "weekly_revenue": weekly_revenue,
        "best_selling": best_selling,
        "low_stock_items": low_stock_items,
        "order_count_today": order_count_today,
        "payment_breakdown":payment_breakdown
    }
    return render(request,"reports/dashboard.html",context)