from decimal import Decimal, InvalidOperation
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST
from billing.models import Invoice
from .models import Payment
from orders.models import Order
from .khalti import get_payment_url, lookup_khalti_api
from django.contrib import messages
from django.urls import reverse
from notifications.models import Notification
from accounts.models import User
from tables.models import Table



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


def _initiate_khalti_payment(request, order):
    payment_url_data = get_payment_url(
        url=request.build_absolute_uri(reverse("payments:khalti_callback", args=[order.pk])),
        website_url=request.build_absolute_uri("/"),
        amount=int(order.grand_total * 100),
        purchase_order_id=str(order.pk),
        purchase_order_name=f"CafeFlow Order #{order.pk}",
        name=order.contact_name or (order.customer.name if order.customer else "Guest"),
        email=order.customer.email if order.customer else "",
        phone=order.contact_phone or (order.customer.phone if order.customer else ""),
    )
    # No Invoice or Payment created here anymore — only on confirmed success in khalti_callback.
    return payment_url_data.get("payment_url")


@login_required
def khalti_initiate(request, order_pk):
    order = get_object_or_404(Order, pk=order_pk)
    payment_url = _initiate_khalti_payment(request, order)

    if payment_url:
        return render(request, "payments/khalti_redirect.html", {"payment_url": payment_url})

    messages.error(request, "Something went wrong starting the payment. Please try again.")
    return redirect("orders:order_detail", pk=order.pk)


def khalti_callback(request, order_pk):
    order = get_object_or_404(Order, pk=order_pk)
    pidx = request.GET.get("pidx")

    if not pidx:
        order.status = Order.Status.CANCELLED
        order.save(update_fields=["status"])
        messages.error(request, "Payment was not completed. Your order has been cancelled.")
        return render(request, "payments/khalti_result.html", {"order": order, "payment": None})

    result = lookup_khalti_api(pidx)

    if result.get("status") == "Completed":
        invoice, _ = Invoice.objects.get_or_create(order=order)
        payment = Payment.objects.create(
            invoice=invoice,
            payment_method=Payment.Method.KHALTI,
            pidx=pidx,
            transaction_id=request.GET.get("transaction_id", ""),
            status=Payment.Status.SUCCESS,
            amount=order.grand_total,
        )

        invoice.is_paid = True
        invoice.save(update_fields=["is_paid"])

        order.send_to_kitchen()

        for staff in User.objects.filter(role__in=[User.Role.FRONT_DESK, User.Role.MANAGER]):
            Notification.objects.create(
                recipient=staff,
                notification_type=Notification.Type.PAYMENT_RECEIVED,
                message=f"Online order #{order.pk} paid via Khalti (Rs.{order.grand_total}) — sent to kitchen.",
            )
    else:
        payment = None
        order.status = Order.Status.CANCELLED
        order.save(update_fields=["status"])

        if order.table and order.table.status == Table.Status.OCCUPIED:
            order.table.mark_available()

    return render(request, "payments/khalti_result.html", {"order": order, "payment": payment})