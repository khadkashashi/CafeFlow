import requests
from django.conf import settings


def initiate_khalti_payment(order, return_url):
    url = f"{settings.KHALTI_BASE_URL}/epayment/initiate/"
    headers = {"Authorization": f"Key {settings.KHALTI_SECRET_KEY}"}
    payload = {
        "return_url": return_url,
        "website_url": settings.SITE_BASE_URL,
        "amount": int(order.grand_total * 100),  # Khalti expects paisa, not rupees
        "purchase_order_id": str(order.pk),
        "purchase_order_name": f"CafeFlow Order #{order.pk}",
    }
    response = requests.post(url, headers=headers, json=payload, timeout=15)
    response.raise_for_status()
    return response.json()  # contains "payment_url" and "pidx"


def verify_khalti_payment(pidx):
    url = f"{settings.KHALTI_BASE_URL}/epayment/lookup/"
    headers = {"Authorization": f"Key {settings.KHALTI_SECRET_KEY}"}
    response = requests.post(url, headers=headers, json={"pidx": pidx}, timeout=15)
    response.raise_for_status()
    return response.json()  # contains "status": "Completed"/"Pending"/etc.