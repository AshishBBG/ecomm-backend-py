"""
Cart model (one row per user's product in cart).

Notes:
- Uses SQLAlchemy 2.0 annotated declarative style (Mapped, mapped_column).
- Adds a uniqueness constraint on (user_id, product_id) to avoid duplicate cart lines.
- Uses server_default for quantity so DB and ORM defaults align.
- Provides a to_dict() helper for JSON responses.
"""

from __future__ import annotations
from typing import Any, Dict, Optional

from datetime import datetime
from sqlalchemy import func, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.extensions import db


class Cart(db.Model):
    __tablename__ = "cart"  # keeping your original table name; consider 'cart_items' if you prefer
    __table_args__ = (
        UniqueConstraint("user_id", "product_id", name="uq_cart_user_product"),
        db.Index("ix_cart_user_id", "user_id"),
        db.Index("ix_cart_product_id", "product_id"),
    )

    id: Mapped[int] = mapped_column(db.Integer, primary_key=True)

    user_id: Mapped[int] = mapped_column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    product_id: Mapped[int | None] = mapped_column(db.Integer, db.ForeignKey("products.id", ondelete="SET NULL"), nullable=True, index=True)

    quantity: Mapped[int] = mapped_column(db.Integer, nullable=False, server_default="1")

    created_at: Mapped[datetime] = mapped_column(
        db.DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        db.DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    # Relationships (use back_populates for bi-directional mapping)
    user: Mapped["User"] = relationship("User", back_populates="cart_items", lazy="select")
    product: Mapped["Product"] = relationship("Product", back_populates="cart_items", lazy="select")

    def __repr__(self) -> str:  # pragma: no cover - trivial
        return f"<Cart id={self.id} user_id={self.user_id} product_id={self.product_id} qty={self.quantity}>"

    def to_dict(self, include_relations: bool = False) -> Dict[str, Any]:
        """
        Serialize cart row.

        Args:
            include_relations: if True, include nested product and/or user dicts (one-level).
        """
        data: Dict[str, Any] = {
            "id": self.id,
            "user_id": self.user_id,
            "product_id": self.product_id,
            "quantity": int(self.quantity) if self.quantity is not None else None,
            "created_at": self.created_at.isoformat() if isinstance(self.created_at, datetime) else None,
            "updated_at": self.updated_at.isoformat() if isinstance(self.updated_at, datetime) else None,
        }

        if include_relations:
            if hasattr(self, "product") and self.product is not None:
                data["product"] = self.product.to_dict(include_category=True) if hasattr(self.product, "to_dict") else {"id": self.product_id}
            if hasattr(self, "user") and self.user is not None:
                data["user"] = {"id": self.user.id, "username": getattr(self.user, "username", None)}

        return data
