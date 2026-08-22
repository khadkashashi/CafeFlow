from decimal import Decimal, InvalidOperation
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST
from billing.models import Invoice
from .models import Payment


@login_required
def payment_screen(request, invoice_pk):
    invoice = get_object_or_404(Invoice, pk=invoice_pk)
    if invoice.is_paid:
        return redirect("billing:invoice_detail", pk=invoice.pk)
    customer = invoice.order.customer
    context = {
        "invoice": invoice,
        "methods": Payment.Method.choices,
        "customer": customer,
        "point_value": settings.LOYALTY_POINT_VALUE,
    }

    if request.method == "POST":
        method = request.POST.get("payment_method")
        valid_methods = dict(Payment.Method.choices)
        if method not in valid_methods:
            context["error"] = "Please select a valid payment method."
            return render(request, "payments/payment_screen.html", context)
        try:
            received = Decimal(request.POST.get("received", "0"))
        except InvalidOperation:
            context["error"] = "Enter a valid amount."
            return render(request, "payments/payment_screen.html", context)
        if received < invoice.grand_total:
            context["error"] = f"Amount received (Rs.{received}) is less than the total (Rs.{invoice.grand_total})."
            return render(request, "payments/payment_screen.html", context)
        Payment.objects.create(
            invoice=invoice,
            payment_method=method,
            amount=invoice.grand_total,
            status=Payment.Status.SUCCESS,
        )

        change = received - invoice.grand_total
        return render(request, "payments/payment_success.html", {"invoice": invoice, "received": received, "change": change, "method": method})
    return render(request, "payments/payment_screen.html", context)


@login_required
@require_POST
def redeem_points(request, invoice_pk):
    invoice = get_object_or_404(Invoice, pk=invoice_pk)
    customer = invoice.order.customer
    if not invoice.is_paid and customer:
        try:
            points = int(request.POST.get("redeem_points", "0"))
        except ValueError:
            points = 0
        points = max(0, min(points, customer.loyalty_points))
        redemption_value = min(points * settings.LOYALTY_POINT_VALUE, invoice.grand_total)
        actual_points_used = int(redemption_value // settings.LOYALTY_POINT_VALUE) if settings.LOYALTY_POINT_VALUE else 0
        if actual_points_used > 0:
            invoice.discount += redemption_value
            invoice.grand_total -= redemption_value
            invoice.save(update_fields=["discount", "grand_total"])
            customer.loyalty_points -= actual_points_used
            customer.save(update_fields=["loyalty_points"])

    return redirect("payments:payment_screen", invoice_pk=invoice.pk)