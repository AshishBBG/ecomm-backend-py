from app.extensions import db
from app.models.product import Product
from app.utils.response import format_model


# -----------------------------
# GET ALL PRODUCTS
# -----------------------------
def get_products():
    products = Product.query.all()
    return [format_model(p) for p in products]


# -----------------------------
# GET PRODUCT BY ID
# -----------------------------
def get_product_by_id(product_id):
    product = Product.query.get(product_id)
    return format_model(product) if product else None


# -----------------------------
# CREATE PRODUCT
# -----------------------------
def create_product(data):
    try:
        product = Product(
            name=data.get("name"),
            description=data.get("description"),
            price=data.get("price"),
            stock=data.get("stock", 0),
            category_id=data.get("category_id")
        )
        db.session.add(product)
        db.session.commit()
        return format_model(product)

    except Exception as e:
        db.session.rollback()
        raise e


# -----------------------------
# UPDATE PRODUCT
# -----------------------------
def update_product(product_id, data):
    product = Product.query.get(product_id)
    if not product:
        return None

    try:
        if "name" in data:
            product.name = data["name"]
        if "description" in data:
            product.description = data["description"]
        if "price" in data:
            product.price = data["price"]
        if "stock" in data:
            product.stock = data["stock"]
        if "category_id" in data:
            product.category_id = data["category_id"]

        db.session.commit()
        return format_model(product)

    except Exception as e:
        db.session.rollback()
        raise e


# -----------------------------
# DELETE PRODUCT
# -----------------------------
def delete_product(product_id):
    product = Product.query.get(product_id)
    if not product:
        return False

    try:
        db.session.delete(product)
        db.session.commit()
        return True

    except Exception as e:
        db.session.rollback()
        raise e
