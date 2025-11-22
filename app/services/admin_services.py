from app.models.user import User
from app.models.order import Order

def get_all_users():
    users = User.query.all()
    return [{
        "id": u.id,
        "email": u.email,
        "is_admin": getattr(u, "is_admin", False)
    } for u in users]


def get_all_orders():
    orders = Order.query.all()
    return [{"id": o.id, "user_id": o.user_id, "total_amount": o.total_amount, "status": o.status} for o in orders]
