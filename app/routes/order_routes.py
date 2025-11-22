from flask import Blueprint, request
from app.services.order_services import create_order, get_orders_by_user
from app.utils.response import success_response, error_response

order_bp = Blueprint("order", __name__)

@order_bp.route("/", methods=["POST"])
def place_order():
    data = request.get_json() or {}
    order = create_order(data)
    if order:
        return success_response(order, 201)
    return error_response("Failed to create order", 400)

@order_bp.route("/user/<int:user_id>", methods=["GET"])
def list_orders(user_id):
    orders = get_orders_by_user(user_id)
    return success_response(orders)
