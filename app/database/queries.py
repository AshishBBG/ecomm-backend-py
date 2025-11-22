from app.extensions import db
from app.models.user import User
from app.models.product import Product

# Example: get user by email
def get_user_by_email(email):
    return User.query.filter_by(email=email).first()

# Example: get product by ID
def get_product_by_id(product_id):
    return Product.query.filter_by(id=product_id).first()

# Example: get all products
def get_all_products():
    return Product.query.all()
