from django.shortcuts import render,get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from accounts.decorators import role_required
from accounts.models import User
from tables.models import Table
from .forms import OrderForm, OrderItemFormSet
from .models import Order

# Create your views here.

@login_required
@role_required(User.Role.WAITER, User.Role.FRONT_DESK, User.Role.MANAGER)
def pos_screen(request):
    if request.method =="POST":
        order_form =OrderForm(request.POST)
        if order_form.is_valid():
            order= order_form.save(commit=False)
            order.waiter= request.user
            order.save()
            formset = OrderItemFormSet(request.POST, instance=order)
            if formset.is_valid():
                formset.save()
                order.recalculate_totals()
                return redirect("orders:order_detail", pk=order.pk)
        else:
            formset = OrderItemFormSet(request.POST)
    else:
        order_form = OrderForm()
        formset = OrderItemFormSet()
    tables = Table.objects.filter(status=Table.Status.AVAILABLE)
    return render(request,"orders/pos_screen.html",{"order_form": order_form, "formset": formset, "tables": tables})


@login_required
def order_detail(request, pk):
    order = get_object_or_404(Order, pk=pk)
    return render(request, "orders/order_detail.html", {"order": order})

STATUS_STEPS = ["PENDING", "PREPARING", "READY", "COMPLETED"]

@login_required
def track_order(request, pk):
    order = get_object_or_404(Order, pk=pk)
    current_index = STATUS_STEPS.index(order.status) if order.status in STATUS_STEPS else -1
    return render(request, "orders/track_order.html", { "order": order, "steps": STATUS_STEPS, "current_index": current_index})