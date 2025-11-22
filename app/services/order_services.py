from app.errors import ServiceError
from app.extensions import db
from app.models.order import Order
from app.models.cart import Cart
from app.models.product import Product

def create_order(data):
    user_id = data.get("user_id")
    cart_items = Cart.query.filter_by(user_id=user_id).all()
    if not cart_items:
        return None

    total_amount = sum(item.product.price * item.quantity for item in cart_items)
    order = Order(user_id=user_id, total_amount=total_amount, status="pending")
    db.session.add(order)
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        raise ServiceError(f"Database commit failed: {e}")

    # Optional: clear cart after creating order
    for item in cart_items:
        db.session.delete(item)
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        raise ServiceError(f"Database commit failed: {e}")

    return {"order_id": order.id, "total_amount": total_amount, "status": order.status}

def get_orders_by_user(user_id):
    orders = Order.query.filter_by(user_id=user_id).all()
    return [{"id": o.id, "total_amount": o.total_amount, "status": o.status} for o in orders]
