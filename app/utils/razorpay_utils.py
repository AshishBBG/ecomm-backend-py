import razorpay
from flask import current_app

def create_client():
    return razorpay.Client(
        auth=(current_app.config["RAZORPAY_KEY"], current_app.config["RAZORPAY_SECRET"])
    )

def create_order(amount, currency="INR", receipt=None):
    client = create_client()
    order_data = {
        "amount": int(amount * 100),  # amount in paise
        "currency": currency,
        "receipt": receipt or "order_rcptid_1"
    }
    return client.order.create(order_data)

def verify_payment_signature(payment_id, order_id, signature):
    client = create_client()
    params_dict = {
        "razorpay_order_id": order_id,
        "razorpay_payment_id": payment_id,
        "razorpay_signature": signature
    }
    return client.utility.verify_payment_signature(params_dict)
