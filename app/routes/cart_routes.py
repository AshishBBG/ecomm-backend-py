from flask import Blueprint, request
from app.services.cart_services import add_to_cart, remove_from_cart, get_user_cart
from app.utils.response import success_response, error_response

# ❗️ IMPORTANT: No prefix here
cart_bp = Blueprint("cart", __name__)

@cart_bp.route("/", methods=["GET"])
def view_cart():
    user_id = request.args.get("user_id")
    cart_items = get_user_cart(user_id)
    return success_response(cart_items)

@cart_bp.route("/add", methods=["POST"])
def add_item():
    data = request.get_json() or {}
    item = add_to_cart(data)
    if item:
        return success_response(item, 201)
    return error_response("Failed to add item", 400)

@cart_bp.route("/remove", methods=["DELETE"])
def remove_item():
    data = request.get_json() or {}
    success = remove_from_cart(data)
    if success:
        return success_response({"message": "Item removed"})
    return error_response("Failed to remove item", 400)
