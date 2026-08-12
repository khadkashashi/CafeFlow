from django.shortcuts import render,get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import KitchenOrder

# Create your views here.
@login_required
def kitchen_dashboard(request):
    queued = KitchenOrder.objects.filter(status=KitchenOrder.Status.QUEUED).select_related("order", "order__table")
    in_progress = KitchenOrder.objects.filter(status=KitchenOrder.Status.IN_PROGRESS).select_related("order", "order__table")
    done = KitchenOrder.objects.filter(status=KitchenOrder.Status.DONE).select_related("order", "order__table")[:10]

    return render(request,"kitchen/dashboard.html",{"queued": queued, "in_progress": in_progress, "done": done})


@login_required
def start_cooking(request, pk):
    ticket = get_object_or_404(KitchenOrder, pk=pk)
    ticket.start(chef=request.user)
    return redirect("kitchen:dashboard")


@login_required
def mark_ready(request, pk):
    ticket = get_object_or_404(KitchenOrder, pk=pk)
    ticket.complete()
    return redirect("kitchen:dashboard")