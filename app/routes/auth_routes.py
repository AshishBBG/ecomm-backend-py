from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.services.auth_services import create_user, authenticate_user, get_user_by_id
from app.utils.response import success_response, error_response

auth_bp = Blueprint("auth", __name__)


# REGISTER USER

@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.get_json() or {}
    name = data.get("name")
    email = data.get("email")
    password = data.get("password")
    
    if not email or not password or not name:
        return error_response("Name, Email and password are required", 400)

    user = create_user(name, email, password)
    return success_response({"id": user.id, "name": user.username ,"email": user.email}, 201)



# LOGIN USER

@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json() or {}
    email = data.get("email")
    password = data.get("password")
   
    user, token = authenticate_user(email, password)
    if not user:
        return error_response("Invalid credentials", 401)

    return success_response({"access_token": token})


# GET LOGGED-IN USER

@auth_bp.route("/me", methods=["GET"])
@jwt_required()
def get_me():
    user_id = get_jwt_identity()
    user = get_user_by_id(user_id)   # This returns a dict

    if not user:
        return error_response("User not found", 404)

    return success_response({
        "id": user["id"],
        "email": user["email"],
        "is_admin": user.get("is_admin")
    })
