import json
import os

import requests


def get_payment_url(**kwargs):
    url = "https://dev.khalti.com/api/v2/epayment/initiate/"
    key = os.environ.get("KHALTI_SECRET_KEY")
    payload = {
        "return_url": kwargs.get("url"),
        "website_url": kwargs.get("website_url"),
        "amount": kwargs.get("amount"),
        "purchase_order_id": kwargs.get("purchase_order_id"),
        "purchase_order_name": kwargs.get("purchase_order_name"),
        "customer_info": {
            "name": kwargs.get("name"),
            "email": kwargs.get("email", "test@cafeflow.com"),
            "phone": kwargs.get("phone", "9800000123"),
        },
    }
    headersList = {"Accept": "*/*", "Content-Type": "application/json", "Authorization": f"Key {key} "}
    r = requests.post(url=url, headers=headersList, data=json.dumps(payload))
    return r.json()


def lookup_khalti_api(pidx):
    url = "https://dev.khalti.com/api/v2/epayment/lookup/"
    key = os.environ.get("KHALTI_SECRET_KEY")
    payload = {"pidx": pidx}
    headersList = {"Accept": "*/*", "Content-Type": "application/json", "Authorization": f"Key {key} "}
    r = requests.post(url=url, headers=headersList, data=json.dumps(payload))
    return r.json()