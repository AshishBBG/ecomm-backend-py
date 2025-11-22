from flask import Blueprint, request
from app.services.product_services import (
    get_products,
    get_product_by_id,
    create_product,
    update_product,
    delete_product
)
from app.utils.response import success_response, error_response

product_bp = Blueprint("product", __name__)

# ---------------------------
# GET ALL PRODUCTS
# ---------------------------
@product_bp.route("/", methods=["GET"])
def list_products():
    products = get_products()
    return success_response(products)

# ---------------------------
# CREATE PRODUCT
# ---------------------------
@product_bp.route("/", methods=["POST"])
def add_product():
    data = request.get_json() or {}
    product = create_product(data)
    if product:
        return success_response(product, 201)
    return error_response("Failed to create product", 400)

# ---------------------------
# GET PRODUCT BY ID
# ---------------------------
@product_bp.route("/<int:product_id>", methods=["GET"])
def get_product(product_id):
    product = get_product_by_id(product_id)
    if product:
        return success_response(product)
    return error_response("Product not found", 404)

# ---------------------------
# UPDATE PRODUCT BY ID
# ---------------------------
@product_bp.route("/<int:product_id>", methods=["PUT"])
def edit_product(product_id):
    data = request.get_json() or {}
    updated = update_product(product_id, data)
    if updated:
        return success_response(updated)
    return error_response("Product not found", 404)

# ---------------------------
# DELETE PRODUCT BY ID
# ---------------------------
@product_bp.route("/<int:product_id>", methods=["DELETE"])
def remove_product(product_id):
    deleted = delete_product(product_id)
    if deleted:
        return success_response({"deleted": product_id})
    return error_response("Product not found", 404)
