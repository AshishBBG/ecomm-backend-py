"""
User model (SQLAlchemy 2.0 style).

Uses explicit Mapped[...] annotations to satisfy SQLAlchemy's annotated declarative rules.
Provides secure password handling via Flask-Bcrypt.
"""

from __future__ import annotations
from typing import Any, Dict, Optional, List

from datetime import datetime
from sqlalchemy import func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.extensions import db, bcrypt


class User(db.Model):
    __tablename__ = "users"
    __table_args__ = (
        db.Index("ix_users_email", "email"),
        db.Index("ix_users_username", "username"),
    )

    id: Mapped[int] = mapped_column(db.Integer, primary_key=True)
    username: Mapped[str] = mapped_column(db.String(120), unique=False, nullable=False)
    email: Mapped[str] = mapped_column(db.String(255), unique=True, nullable=False, index=True)
    password_hash: Mapped[str] = mapped_column(db.String(255), nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        db.DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        db.DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    # Relationship to Cart items (one-to-many)
    cart_items: Mapped[List["Cart"]] = relationship(
        "Cart",
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="select",
    )
    orders: Mapped[List["Order"]] = relationship(
        "Order",
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="select"
    )

    def __repr__(self) -> str:
        return f"<User id={self.id} username={self.username!r} email={self.email!r}>"

    # Password helpers
    @property
    def password(self) -> None:
        raise AttributeError("Password is write-only. Use set_password() to set it.")

    @password.setter
    def password(self, raw_password: str) -> None:
        if not raw_password:
            raise ValueError("Password must not be empty.")
        # bcrypt.generate_password_hash returns bytes; decode to str for storage
        self.password_hash = bcrypt.generate_password_hash(raw_password).decode("utf-8")

    def set_password(self, raw_password: str) -> None:
        self.password = raw_password

    def check_password(self, raw_password: str) -> bool:
        if not self.password_hash:
            return False
        return bcrypt.check_password_hash(self.password_hash, raw_password)

    # Serialization
    def to_dict(self, include_relationships: bool = False, exclude: Optional[set] = None) -> Dict[str, Any]:
        exclude = set(exclude or set())
        exclude.add("password_hash")

        data: Dict[str, Any] = {}
        for col in self.__table__.columns:
            name = col.name
            if name in exclude:
                continue
            val = getattr(self, name)
            # If datetime, convert to ISO format for safety
            if isinstance(val, datetime):
                data[name] = val.isoformat()
            else:
                data[name] = val

        if include_relationships:
            if hasattr(self, "cart_items"):
                data["cart_items"] = [ci.to_dict(include_relationships=False) for ci in getattr(self, "cart_items", [])]

        return data
