from app.errors import ServiceError
from app.extensions import db
from app.models.category import Category

def get_categories():
    categories = Category.query.all()
    return [{"id": c.id, "name": c.name} for c in categories]

def create_category(name):
    category = Category(name=name)
    db.session.add(category)
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        raise ServiceError(f"Database commit failed: {e}")
    return {"id": category.id, "name": category.name}


def get_category_by_id(category_id):
    return Category.query.get(category_id)

def update_category(category_id, name):
    category = Category.query.get(category_id)
    if not category:
        return None
    category.name = name
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        raise ServiceError(f"Database commit failed: {e}")
    return {"id": category.id, "name": category.name}

def delete_category(category_id):
    category = Category.query.get(category_id)
    if not category:
        return False
    try:
        db.session.delete(category)
        db.session.commit()
        return True
    except Exception as e:
        db.session.rollback()
        raise ServiceError(f"Database commit failed: {e}")
