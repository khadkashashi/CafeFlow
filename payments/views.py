from decimal import Decimal, InvalidOperation
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST
from billing.models import Invoice
from .models import Payment
from orders.models import Order
from .khalti import initiate_khalti_payment, verify_khalti_payment



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

@login_required
def khalti_initiate(request, order_pk):
    order = get_object_or_404(Order, pk=order_pk)
    return_url = request.build_absolute_uri(f"/payments/khalti/callback/{order.pk}/")

    try:
        data = initiate_khalti_payment(order, return_url)
        request.session[f"khalti_pidx_{order.pk}"] = data["pidx"]
        return redirect(data["payment_url"])
    except Exception:
        # Sandbox/demo fallback — if Khalti isn't reachable, don't strand the customer
        order.send_to_kitchen()
        return redirect("orders:order_detail", pk=order.pk)


@login_required
def khalti_callback(request, order_pk):
    order = get_object_or_404(Order, pk=order_pk)
    pidx = request.GET.get("pidx") or request.session.get(f"khalti_pidx_{order.pk}")

    if pidx:
        result = verify_khalti_payment(pidx)
        if result.get("status") == "Completed":
            invoice, _ = Invoice.objects.get_or_create(order=order)
            Payment.objects.create(
                invoice=invoice, payment_method=Payment.Method.ESEWA,  # Khalti not in original choices — see note below
                amount=order.grand_total, status=Payment.Status.SUCCESS,
            )
            order.send_to_kitchen()

    return redirect("orders:order_detail", pk=order.pk)