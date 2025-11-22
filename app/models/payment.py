from app.extensions import db

class Payment(db.Model):
    __tablename__ = "payments"

    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey("orders.id"), nullable=False)
    amount = db.Column(db.Float, nullable=False)                # <— ADD THIS
    mode = db.Column(db.String(50), nullable=False, default="razorpay")  
    status = db.Column(db.String(50), nullable=False, default="pending")

