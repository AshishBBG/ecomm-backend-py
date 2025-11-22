from flask import Blueprint, request
from app.services.payment_services import create_payment, verify_payment
from app.utils.response import success_response, error_response

payment_bp = Blueprint("payment", __name__)

@payment_bp.route("/", methods=["POST"])
def make_payment():
    data = request.get_json() or {}
    payment = create_payment(data)
    if payment:
        return success_response(payment, 201)
    return error_response("Payment failed", 400)

@payment_bp.route("/verify", methods=["POST"])
def verify():
    data = request.get_json() or {}
    success = verify_payment(data)
    if success:
        return success_response({"message": "Payment verified"})
    return error_response("Payment verification failed", 400)
