from flask import Blueprint
from app.services.auth_services import get_user_by_id
from app.utils.response import success_response, error_response

user_bp = Blueprint("user", __name__)

@user_bp.route("/<int:user_id>", methods=["GET"])
def get_user(user_id):
    user = get_user_by_id(user_id)
    if user:
        return success_response(user)
    return error_response("User not found", 404)
