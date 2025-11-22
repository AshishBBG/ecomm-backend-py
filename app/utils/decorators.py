from functools import wraps
from flask import request
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity
from app.utils.response import error_response

def jwt_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            verify_jwt_in_request()
            return f(*args, **kwargs)
        except Exception:
            return error_response("Unauthorized", 401)
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        verify_jwt_in_request()
        user_id = get_jwt_identity()
        from app.models.user import User
        user = User.query.get(user_id)
        if user and user.is_admin:
            return f(*args, **kwargs)
        return error_response("Admin access required", 403)
    return decorated_function
