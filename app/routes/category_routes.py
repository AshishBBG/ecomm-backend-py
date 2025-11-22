from flask import Blueprint, request
from app.services.category_services import (
    get_categories,
    create_category,
    update_category,
    delete_category
)
from app.utils.response import success_response, error_response

# Blueprint with no trailing slash issues
category_bp = Blueprint("category", __name__)

# GET /api/v1/categories
@category_bp.route("", methods=["GET"])
def list_categories():
    categories = get_categories()
    return success_response(categories)

# POST /api/v1/categories
@category_bp.route("", methods=["POST"])
def add_category():
    data = request.get_json() or {}
    name = data.get("name")

    if not name:
        return error_response("Category name required", 400)

    category = create_category(name)

    if category:
        return success_response(category, 201)
    
    return error_response("Failed to create category", 400)

# PUT /api/v1/categories/<id>
@category_bp.route("/<int:category_id>", methods=["PUT"])
def edit_category(category_id):
    data = request.get_json() or {}
    name = data.get("name")

    if not name:
        return error_response("Category name required", 400)

    category = update_category(category_id, name)

    if category:
        return success_response(category)

    return error_response("Category not found", 404)

# DELETE /api/v1/categories/<id>
@category_bp.route("/<int:category_id>", methods=["DELETE"])
def remove_category(category_id):
    ok = delete_category(category_id)

    if ok:
        return success_response({"deleted": category_id})

    return error_response("Category not found", 404)
