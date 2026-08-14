from django.shortcuts import render,get_object_or_404, redirect
from .models import KitchenOrder
from accounts.decorators import role_required
from accounts.models import User

# Create your views here.
@role_required(User.Role.CHEF, User.Role.MANAGER)
def kitchen_dashboard(request):
    queued = KitchenOrder.objects.filter(status=KitchenOrder.Status.QUEUED).select_related("order", "order__table")
    in_progress = KitchenOrder.objects.filter(status=KitchenOrder.Status.IN_PROGRESS).select_related("order", "order__table")
    done = KitchenOrder.objects.filter(status=KitchenOrder.Status.DONE).select_related("order", "order__table")[:10]

    return render(request,"kitchen/dashboard.html",{"queued": queued, "in_progress": in_progress, "done": done})


@role_required(User.Role.CHEF, User.Role.MANAGER)
def start_cooking(request, pk):
    ticket = get_object_or_404(KitchenOrder, pk=pk)
    ticket.start(chef=request.user)
    return redirect("kitchen:dashboard")


@role_required(User.Role.CHEF, User.Role.MANAGER)
def mark_ready(request, pk):
    ticket = get_object_or_404(KitchenOrder, pk=pk)
    ticket.complete()
    return redirect("kitchen:dashboard")