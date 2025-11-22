from flask_jwt_extended import create_access_token as jwt_create_access_token, decode_token


def generate_access_token(user_id):
    """
    Generate a JWT access token for the given user ID.
    Flask-JWT-Extended expects identity to be a STRING.
    """
    return jwt_create_access_token(identity=str(user_id))


def decode_access_token(token):
    """
    Decode token and return user_id (converted back to int if possible)
    """
    try:
        decoded = decode_token(token)
        user_id = decoded.get("sub")
        return int(user_id) if user_id is not None else None
    except Exception:
        return None
