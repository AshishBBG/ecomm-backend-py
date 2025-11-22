"""
Category model.

- Uses SQLAlchemy 2.0 annotated declarative style (Mapped, mapped_column).
- Adds created_at / updated_at timestamps.
- Provides bidirectional relationship to Product via back_populates.
- Adds indexes and a safe to_dict() serializer.
"""

from __future__ import annotations
from typing import Any, Dict, List, Optional

from datetime import datetime
from sqlalchemy import func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.extensions import db


class Category(db.Model):
    __tablename__ = "categories"
    __table_args__ = (
        db.Index("ix_categories_name", "name"),
    )

    id: Mapped[int] = mapped_column(db.Integer, primary_key=True)
    name: Mapped[str] = mapped_column(db.String(120), unique=True, nullable=False, index=True)

    created_at: Mapped[datetime] = mapped_column(
        db.DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        db.DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    # Relationship to Product (one-to-many)
    products: Mapped[List["Product"]] = relationship(
        "Product",
        back_populates="category",
        lazy="select",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:  # pragma: no cover - trivial
        return f"<Category id={self.id} name={self.name!r}>"

    def to_dict(self, include_products: bool = False) -> Dict[str, Any]:
        """
        Convert the category to a dictionary for JSON responses.

        Args:
            include_products: whether to include products list (one-level). Default False to avoid heavy queries.
        """
        data: Dict[str, Any] = {
            "id": self.id,
            "name": self.name,
            "created_at": self.created_at.isoformat() if isinstance(self.created_at, datetime) else None,
            "updated_at": self.updated_at.isoformat() if isinstance(self.updated_at, datetime) else None,
        }

        if include_products:
            # Avoid deep traversal and circular serialization; use Product.to_dict if available
            prods = getattr(self, "products", []) or []
            data["products"] = [
                p.to_dict(include_category=False) if hasattr(p, "to_dict") else {"id": getattr(p, "id", None)}
                for p in prods
            ]

        return data
