from decimal import Decimal, InvalidOperation
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from billing.models import Invoice
from .models import Payment

# Create your views here.
@login_required
def payment_screen(request, invoice_pk):
    invoice = get_object_or_404(Invoice, pk=invoice_pk)
    if invoice.is_paid:
        return redirect("billing:invoice_detail", pk=invoice.pk)
    context = {
        "invoice": invoice, 
        "methods": Payment.Method.choices
        }
    if request.method == "POST":
        method = request.POST.get("payment_method")
        try:
            received = Decimal(request.POST.get("received", "0"))
        except InvalidOperation:
            context["error"] = "Enter a valid amount."
            return render(request, "payments/payment_screen.html", context)
        if received < invoice.grand_total:
            context["error"] = f"Amount received (Rs.{received}) is less than the total (Rs.{invoice.grand_total})."
            return render(request, "payments/payment_screen.html", context)

        Payment.objects.create( invoice=invoice,payment_method=method,amount=invoice.grand_total,status=Payment.Status.SUCCESS)
        change = received - invoice.grand_total
        contexts={
                    "invoice": invoice, 
                    "received": received, 
                    "change": change, 
                    "method": method,
                }
        return render(request, "payments/payment_success.html", contexts)
    return render(request, "payments/payment_screen.html", context)