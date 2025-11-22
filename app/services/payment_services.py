from app.errors import ServiceError
from app.extensions import db
from app.models.payment import Payment
from app.models.order import Order

# For simplicity, mock Razorpay integration
def create_payment(data):
    order_id = data.get("order_id")
    amount = data.get("amount")
    mode = data.get("mode") or "razorpay"

    payment = Payment(
        order_id=order_id,
        amount=amount,
        mode=mode,
        status="pending"
    )

    db.session.add(payment)
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        raise ServiceError(f"Database commit failed: {e}")

    return {
        "payment_id": payment.id,
        "order_id": order_id,
        "amount": amount,
        "mode": mode,
        "status": payment.status
    }

def verify_payment(data):
    payment_id = data.get("payment_id")
    payment = Payment.query.get(payment_id)

    if not payment:
        return False

    # Mark payment as paid
    payment.status = "paid"

    # ALSO update the order status
    order = Order.query.get(payment.order_id)
    if order:
        order.status = "paid"

    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        raise ServiceError(f"Database commit failed: {e}")

    return True
