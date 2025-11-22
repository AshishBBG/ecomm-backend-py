# Models package initialization
from flask_sqlalchemy import SQLAlchemy

# Do NOT import models yet — SQLAlchemy must initialize first
# db = SQLAlchemy() is in extensions.py

from app.models.user import User
from app.models.product import Product
from app.models.category import Category
from app.models.cart import Cart
from app.models.order import Order
from app.models.payment import Payment

