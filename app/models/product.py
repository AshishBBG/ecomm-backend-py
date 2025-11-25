"""
Product model.

Improvements:
- Uses SQLAlchemy 2.0 typed ORM (Mapped and mapped_column).
- Uses Numeric() for price to avoid floating-point precision issues.
- Adds created_at / updated_at timestamps.
- Adds indexes for name and category_id.
- Adds relationship to Category with back_populates.
- Provides a clean to_dict() serializer.
"""

from __future__ import annotations
from typing import Any, Dict
from datetime import datetime
from sqlalchemy import func, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.extensions import db


class Product(db.Model):
    __tablename__ = "products"
    __table_args__ = (
        db.Index("ix_products_name", "name"),
        db.Index("ix_products_category_id", "category_id"),
    )

    # -------------------------
    # Columns
    # -------------------------
    id: Mapped[int] = mapped_column(db.Integer, primary_key=True)

    name: Mapped[str] = mapped_column(db.String(255), nullable=False, index=True)

    description: Mapped[str | None] = mapped_column(db.Text, nullable=True)

    # Numeric price for safety (10 digits, 2 decimals)
    price: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)

    stock: Mapped[int] = mapped_column(db.Integer, nullable=False, default=0, server_default="0")

    category_id: Mapped[int | None] = mapped_column(
        db.Integer, db.ForeignKey("categories.id", ondelete="SET NULL"), nullable=True
    )

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        db.DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        db.DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    # -------------------------
    # Relationships
    # -------------------------
    category = relationship("Category", back_populates="products", lazy="select")
    cart_items = relationship("Cart", back_populates="product", cascade="all, delete-orphan")
    # -------------------------
    # Representation
    # -------------------------
    def __repr__(self) -> str:  # pragma: no cover
        return f"<Product id={self.id} name={self.name!r} price={self.price}>"

    # -------------------------
    # Serialization
    # -------------------------
    def to_dict(self, include_category: bool = False) -> Dict[str, Any]:
        """
        Convert the product to a dictionary for JSON responses.
        Numeric fields like price remain decimal until handled by response serializer.
        """
        data = {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "price": float(self.price) if self.price is not None else None,
            "stock": self.stock,
            "category_id": self.category_id,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

        if include_category and self.category:
            data["category"] = self.category.to_dict(include_products=False)

        return data
