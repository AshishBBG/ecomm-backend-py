"""
Order model.

- SQLAlchemy 2.0 style (Mapped, mapped_column)
- total_amount stored as Numeric(12, 2) to avoid float precision issues
- status is an Enum with sensible defaults
- timestamps and relationships included
"""

from __future__ import annotations
from typing import Any, Dict, List, Optional
from datetime import datetime
import enum

from sqlalchemy import func, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.extensions import db


class OrderStatus(str, enum.Enum):
    PENDING = "pending"
    PAID = "paid"
    SHIPPED = "shipped"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"


class Order(db.Model):
    __tablename__ = "orders"
    __table_args__ = (
        db.Index("ix_orders_user_id", "user_id"),
    )

    id: Mapped[int] = mapped_column(db.Integer, primary_key=True)

    user_id: Mapped[int | None] = mapped_column(db.Integer, db.ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)

    # Use Numeric for currency: precision 12, scale 2 (support up to ~999,999,999.99)
    total_amount: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)

    # Use a DB enum when possible; SQLAlchemy will create a CHECK/ENUM depending on backend
    status: Mapped[OrderStatus] = mapped_column(
        db.Enum(OrderStatus, name="order_status", native_enum=False),
        nullable=False,
        server_default=OrderStatus.PENDING.value,
    )

    created_at: Mapped[datetime] = mapped_column(
        db.DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        db.DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="orders", lazy="select")

    # If you have an OrderItem model, use this; it should declare order = relationship("Order", back_populates="order_items")
    order_items: Mapped[List["OrderItem"]] = relationship(
        "OrderItem",
        back_populates="order",
        lazy="select",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:  # pragma: no cover - trivial
        return f"<Order id={self.id} user_id={self.user_id} total={self.total_amount} status={self.status}>"

    # Business helpers
    def update_status(self, new_status: OrderStatus) -> None:
        """Safely update order status (use enum values)."""
        if isinstance(new_status, str):
            new_status = OrderStatus(new_status)
        self.status = new_status

    # Serialization
    def to_dict(self, include_items: bool = False, include_user: bool = False) -> Dict[str, Any]:
        """
        Serialize the order.
        - include_items: include order_items (one level); may be heavy if many items.
        - include_user: include minimal user info (id, username).
        """
        data: Dict[str, Any] = {
            "id": self.id,
            "user_id": self.user_id,
            "total_amount": float(self.total_amount) if self.total_amount is not None else None,
            "status": self.status.value if isinstance(self.status, enum.Enum) else str(self.status),
            "created_at": self.created_at.isoformat() if isinstance(self.created_at, datetime) else None,
            "updated_at": self.updated_at.isoformat() if isinstance(self.updated_at, datetime) else None,
        }

        if include_items:
            items = getattr(self, "order_items", []) or []
            data["order_items"] = [
                item.to_dict(include_product=True) if hasattr(item, "to_dict") else {"id": getattr(item, "id", None)}
                for item in items
            ]

        if include_user and hasattr(self, "user") and self.user is not None:
            data["user"] = {"id": self.user.id, "username": getattr(self.user, "username", None)}
 
        return data

# ==========================================
# PASTE THIS AT THE BOTTOM OF app/models/order.py
# ==========================================

class OrderItem(db.Model):
    __tablename__ = "order_items"
    __table_args__ = (
        db.Index("ix_order_items_order_id", "order_id"),
        db.Index("ix_order_items_product_id", "product_id"),
    )

    id: Mapped[int] = mapped_column(db.Integer, primary_key=True)

    # Link to the Order
    order_id: Mapped[int] = mapped_column(
        db.Integer, 
        db.ForeignKey("orders.id", ondelete="CASCADE"), 
        nullable=False
    )

    # Link to the Product
    product_id: Mapped[int | None] = mapped_column(
        db.Integer, 
        db.ForeignKey("products.id", ondelete="SET NULL"), 
        nullable=True
    )

    quantity: Mapped[int] = mapped_column(db.Integer, default=1, nullable=False)
    
    # Store price at moment of purchase (so it doesn't change if product price changes later)
    price: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)

    # Relationships
    order: Mapped["Order"] = relationship("Order", back_populates="order_items")
    product: Mapped["Product"] = relationship("Product")

    # Serialization
    def to_dict(self, include_product: bool = False) -> Dict[str, Any]:
        data = {
            "id": self.id,
            "order_id": self.order_id,
            "product_id": self.product_id,
            "quantity": self.quantity,
            "price": float(self.price) if self.price is not None else 0.0,
        }
        
        if include_product and self.product:
            # Assumes Product model has a to_dict method
            data["product"] = self.product.to_dict()
            
        return data