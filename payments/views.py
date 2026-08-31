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
        amount=int(order.grand_total * 100),  # Khalti wants paisa, not rupees
        purchase_order_id=order.pk,
        purchase_order_name=f"CafeFlow Order #{order.pk}",
        name=order.contact_name or (order.customer.name if order.customer else "Guest"),
        email=order.customer.email if order.customer else "",
        phone=order.contact_phone or (order.customer.phone if order.customer else ""),
    )

    if payment_url_data.get("pidx"):
        invoice, _ = Invoice.objects.get_or_create(order=order)
        Payment.objects.create(
            invoice=invoice,
            payment_method=Payment.Method.KHALTI,
            pidx=payment_url_data["pidx"],
            status=Payment.Status.PENDING,
            amount=order.grand_total,
        )
        return payment_url_data["payment_url"]
    return None


@login_required
def khalti_initiate(request, order_pk):
    order = get_object_or_404(Order, pk=order_pk)
    payment_url = _initiate_khalti_payment(request, order)

    if payment_url:
        return render(request, "payments/khalti_redirect.html", {"payment_url": payment_url, "order": order})

    messages.error(request, "Something went wrong starting the payment. Please try again.")
    return redirect("orders:order_detail", pk=order.pk)


def khalti_callback(request, order_pk):
    order = get_object_or_404(Order, pk=order_pk)
    pidx = request.GET.get("pidx")

    if not pidx:
        messages.error(request, "Something went wrong, please contact staff.")
        return redirect("orders:order_detail", pk=order.pk)

    result = lookup_khalti_api(pidx)
    payment = get_object_or_404(Payment, pidx=pidx)

    if result.get("status") == "Completed":
        payment.status = Payment.Status.SUCCESS
        payment.transaction_id = request.GET.get("transaction_id", "")
        payment.save()
        payment.invoice.check_fully_paid()

        for staff in User.objects.filter(role__in=[User.Role.FRONT_DESK, User.Role.MANAGER]):
            Notification.objects.create(
                recipient=staff,
                notification_type=Notification.Type.PAYMENT_RECEIVED,
                message=f"Online order #{order.pk} paid via Khalti — ready for {order.get_delivery_option_display()}.",
            )
    else:
        payment.status = Payment.Status.FAILED
        payment.save()

    return render(request, "payments/khalti_result.html", {"order": order, "payment": payment})


@login_required
def khalti_initiate(request, order_pk):
    order = get_object_or_404(Order, pk=order_pk)
    payment_url = _initiate_khalti_payment(request, order)

    if payment_url:
        return render(request, "payments/khalti_redirect.html", {"payment_url": payment_url, "order": order})

    messages.error(request, "Something went wrong starting the payment. Please try again.")
    return redirect("orders:order_detail", pk=order.pk)


def khalti_callback(request, order_pk):
    order = get_object_or_404(Order, pk=order_pk)
    pidx = request.GET.get("pidx")

    if not pidx:
        messages.error(request, "Something went wrong, please contact staff.")
        return redirect("orders:order_detail", pk=order.pk)

    result = lookup_khalti_api(pidx)
    payment = get_object_or_404(Payment, pidx=pidx)

    if result.get("status") == "Completed":
        payment.status = Payment.Status.SUCCESS
        payment.transaction_id = request.GET.get("transaction_id", "")
        payment.save()
        payment.invoice.check_fully_paid()

        for staff in User.objects.filter(role__in=[User.Role.FRONT_DESK, User.Role.MANAGER]):
            Notification.objects.create(
                recipient=staff,
                notification_type=Notification.Type.PAYMENT_RECEIVED,
                message=f"Online order #{order.pk} paid via Khalti — ready for {order.get_delivery_option_display()}.",
            )
    else:
        payment.status = Payment.Status.FAILED
        payment.save()

    return render(request, "payments/khalti_result.html", {"order": order, "payment": payment})