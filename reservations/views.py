from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from accounts.decorators import role_required
from accounts.models import User
from customers.models import Customer
from .forms import ReservationForm
from .models import Reservation
from django.shortcuts import get_object_or_404
from tables.models import Table
# Create your views here.
@login_required
def make_reservation(request):
    if request.method == "POST":
        form = ReservationForm(request.POST)
        if form.is_valid():
            customer, _ = Customer.objects.get_or_create(user=request.user,
                defaults={
                    "name": request.user.get_full_name() or request.user.username,
                    "phone": request.user.phone,
                    "email": request.user.email,
                },
            )
            reservation = form.save(commit=False)
            reservation.customer = customer
            reservation.save()
            return redirect("reservations:my_reservations")
    else:
        form = ReservationForm()
    return render(request, "reservations/make_reservation.html", {"form": form})


@login_required
def my_reservations(request):
    customer = Customer.objects.filter(user=request.user).first()
    reservations = Reservation.objects.filter(customer=customer).order_by("-date") if customer else []
    return render(request, "reservations/my_reservations.html", {"reservations": reservations})


@role_required(User.Role.FRONT_DESK, User.Role.MANAGER)
def reservation_list(request):
    reservations = Reservation.objects.exclude(status=Reservation.Status.CANCELLED).select_related("customer", "table")
    tables = Table.objects.all()
    return render(request, "reservations/reservation_list.html", {"reservations": reservations, "tables": tables})


@role_required(User.Role.FRONT_DESK, User.Role.MANAGER)
def confirm_reservation(request, pk):
    reservation = get_object_or_404(Reservation, pk=pk)
    table_id = request.POST.get("table_id")
    if table_id:
        reservation.table = Table.objects.filter(pk=table_id).first()
    reservation.confirm()
    return redirect("reservations:reservation_list")