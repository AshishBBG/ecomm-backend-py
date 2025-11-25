from app.errors import ServiceError
from app.extensions import db, bcrypt
from app.models.user import User
from app.utils.jwt_utils import generate_access_token


def create_user(username, email, password):
    if User.query.filter(User.email == email).first():
        raise ValueError("User with this email already exists")

    password_hash = bcrypt.generate_password_hash(password).decode("utf-8")
    user = User(username=username, email=email, password_hash=password_hash)

    db.session.add(user)
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        raise ServiceError(f"Database commit failed: {e}")

    return user


def authenticate_user(email, password):
    user = User.query.filter_by(email=email).first()

    if user and bcrypt.check_password_hash(user.password_hash, password):

        # JWT FIX → identity must be a STRING
        token = generate_access_token(str(user.id))

        return user, token

    return None, None


def get_user_by_id(user_id):

    # JWT stores identity as string, convert back to int
    try:
        user_id = int(user_id)
    except:
        return None

    user = User.query.get(user_id)

    if user:
        return {
            "id": user.id,
            "email": user.email
        }

    return None
