from flask import Blueprint
from app.services.admin_services import get_all_users, get_all_orders
from app.utils.response import success_response

admin_bp = Blueprint("admin", __name__)

@admin_bp.route("/users", methods=["GET"])
def users():
    return success_response(get_all_users())

@admin_bp.route("/orders", methods=["GET"])
def orders():
    return success_response(get_all_orders())
