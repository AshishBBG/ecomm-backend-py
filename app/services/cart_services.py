from app.errors import ServiceError
from app.extensions import db
from app.models.cart import Cart
from app.models.product import Product

def get_user_cart(user_id):
    items = Cart.query.filter_by(user_id=user_id).all()
    return [
        {
            "product_id": item.product_id,
            "quantity": item.quantity,
            "name": item.product.name,
            "price": item.product.price,
        }
        for item in items
    ]


def add_to_cart(data):
    user_id = data.get("user_id")
    product_id = data.get("product_id")
    quantity = data.get("quantity", 1)

    existing_item = Cart.query.filter_by(user_id=user_id, product_id=product_id).first()
    if existing_item:
        existing_item.quantity += quantity
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            raise ServiceError(f"Database commit failed: {e}")
        return {
            "product_id": existing_item.product_id,
            "quantity": existing_item.quantity,
        }

    cart_item = Cart(user_id=user_id, product_id=product_id, quantity=quantity)
    db.session.add(cart_item)

    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        raise ServiceError(f"Database commit failed: {e}")

    return {"product_id": cart_item.product_id, "quantity": cart_item.quantity}


def remove_from_cart(data):
    user_id = data.get("user_id")
    product_id = data.get("product_id")

    item = Cart.query.filter_by(user_id=user_id, product_id=product_id).first()
    if item:
        db.session.delete(item)
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            raise ServiceError(f"Database commit failed: {e}")
        return True

    return False
