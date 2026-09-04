from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.contrib import messages
from accounts.decorators import role_required
from accounts.models import User
from customers.models import Customer
from .forms import ReservationForm
from .models import Reservation
from django.shortcuts import get_object_or_404
from tables.models import Table
from menu.models import FoodItem
from orders.models import Order, OrderItem
# Create your views here.

@login_required
def make_reservation(request):
    food_items = FoodItem.objects.filter(is_available=True).select_related("category")
    if request.method == "POST":
        form = ReservationForm(request.POST)
        if form.is_valid():
            customer, _ = Customer.objects.get_or_create(
                user=request.user,
                defaults={
                    "name": request.user.get_full_name() or request.user.username,
                    "phone": request.user.phone,
                    "email": request.user.email,
                },
            )
            reservation = form.save(commit=False)
            reservation.customer = customer
            # Optional: pre-order food, saved as a draft order attached to this reservation
            selected_items = [(key.split("_", 1)[1], val) for key, val in request.POST.items()
                if key.startswith("qty_") and val and int(val) > 0
            ]
            if selected_items:
                order = Order.objects.create(customer=customer, source=Order.Source.DINE_IN, status=Order.Status.DRAFT)
                for food_id, qty in selected_items:
                    food = FoodItem.objects.filter(pk=food_id).first()
                    if food:
                        OrderItem.objects.create(order=order, food=food, quantity=int(qty))
                order.recalculate_totals()
                reservation.order = order
            reservation.save()
            return redirect("reservations:my_reservations")
    else:
        form = ReservationForm()

    return render(request, "reservations/make_reservation.html", {"form": form, "food_items": food_items})

@login_required
def my_reservations(request):
    customer = Customer.objects.filter(user=request.user).first()
    reservations = Reservation.objects.filter(customer=customer).order_by("-date") if customer else []
    return render(request, "reservations/my_reservations.html", {"reservations": reservations})


@role_required(User.Role.FRONT_DESK, User.Role.MANAGER)
def reservation_list(request):
    from tables.models import Table
    reservations = Reservation.objects.exclude(status=Reservation.Status.CANCELLED).select_related("customer", "table").order_by("date", "time")
    for r in reservations:
        if r.status == Reservation.Status.PENDING:
            taken_ids = Reservation.objects.filter(
                date=r.date, status=Reservation.Status.CONFIRMED, table__isnull=False
            ).exclude(pk=r.pk).values_list("table_id", flat=True)
            r.available_tables = Table.objects.exclude(pk__in=taken_ids)
    return render(request, "reservations/reservation_list.html", {"reservations": reservations})


@role_required(User.Role.FRONT_DESK, User.Role.MANAGER)
def confirm_reservation(request, pk):
    reservation = get_object_or_404(Reservation, pk=pk)
    table_id = request.POST.get("table_id")
    if not table_id:
        messages.error(request, "Select a table before confirming.")
        return redirect("reservations:reservation_list")

    table = Table.objects.filter(pk=table_id).first()
    reservation.table = table
    reservation.save(update_fields=["table"])
    if reservation.order and table:
        reservation.order.table = table
        reservation.order.save(update_fields=["table"])

    reservation.confirm()
    return redirect("reservations:reservation_list")