"""
Response utilities for consistent JSON responses.

Design:
- Responses use a single envelope:
    {
      "status": "success" | "error",
      "data": <object|null>,
      "error": { "message": "...", "code": "string", "details": {...} } | null,
      "meta": { ... } | null
    }

- success_response(data, status=200, meta=None)
- error_response(message, status=400, code=None, details=None)

- format_model(obj) attempts to convert SQLAlchemy model instances (or lists of them)
  into plain Python dicts. It also handles common scalar types (datetime, Decimal, UUID).
"""

from datetime import date, datetime
from decimal import Decimal
from typing import Any, Dict, Iterable, List, Optional, Union
import uuid

from flask import jsonify
from sqlalchemy.orm import class_mapper
from sqlalchemy.exc import NoInspectionAvailable


# --- Helper: serialize scalar values that are not JSON-native -----------------
def _serialize_value(value: Any) -> Any:
    """Convert non-JSON-native types into JSON-friendly primitives."""
    # None, bool, int, float, str are JSON-serializable already
    if value is None:
        return None
    if isinstance(value, (bool, int, float, str)):
        return value
    if isinstance(value, (datetime, date)):
        # ISO 8601 representation (UTC-awareness responsibility lies elsewhere)
        return value.isoformat()
    if isinstance(value, Decimal):
        # Convert Decimal to string to avoid float precision issues
        # Consumers can parse as needed.
        return str(value)
    if isinstance(value, uuid.UUID):
        return str(value)
    if isinstance(value, bytes):
        # Return base64-like representation for binary data; here convert to str for safety
        try:
            return value.decode("utf-8")
        except Exception:
            return str(value)
    # Fallback to string representation
    return str(value)


# --- Model formatting ---------------------------------------------------------
def _serialize_model_instance(model_obj: Any, include_relationships: bool = False) -> Dict[str, Any]:
    """
    Convert a SQLAlchemy model instance into a dict.

    - Uses the model's mapper to iterate columns; avoids accessing private attrs.
    - Does NOT eagerly traverse relationships unless include_relationships=True.
    """
    data: Dict[str, Any] = {}
    try:
        mapper = class_mapper(model_obj.__class__)
    except NoInspectionAvailable:
        # Not a mappable object; fallback to __dict__ filtering
        for k, v in getattr(model_obj, "__dict__", {}).items():
            if k.startswith("_"):
                continue
            data[k] = _serialize_value(v)
        return data

    # Serialize column attributes
    for column in mapper.columns:
        name = column.key
        try:
            val = getattr(model_obj, name)
        except Exception:
            val = None
        data[name] = _serialize_value(val)

    # Optionally include simple relationships (one level). Beware of N+1 or heavy traversal.
    if include_relationships:
        for rel in mapper.relationships:
            rel_name = rel.key
            try:
                rel_value = getattr(model_obj, rel_name)
            except Exception:
                rel_value = None

            if rel_value is None:
                data[rel_name] = None
            elif isinstance(rel_value, Iterable) and not isinstance(rel_value, (str, bytes, dict)):
                # list-like relationship
                data[rel_name] = [_serialize_model_instance(v, include_relationships=False) for v in rel_value]
            else:
                data[rel_name] = _serialize_model_instance(rel_value, include_relationships=False)

    return data


def format_model(obj: Any, many: Optional[bool] = None, include_relationships: bool = False) -> Any:
    """
    Public formatter:
      - If obj is None -> None
      - If obj is a list/iterable of model instances -> list of dicts
      - If obj is a single model instance -> dict
      - If obj is already a dict -> returned as-is (shallow-serialized)
      - If many is provided it will be used to force behavior for ambiguous iterables.

    Args:
        obj: SQLAlchemy model instance, iterable of instances, dict, or scalar
        many: Optional[bool] to force treat as collection (True) or single (False)
        include_relationships: whether to include related objects (one-level deep)
    """
    if obj is None:
        return None

    # If it's a dict already, assume serializable
    if isinstance(obj, dict):
        # ensure nested values are serializable
        return {k: _serialize_value(v) if not isinstance(v, (dict, list)) else v for k, v in obj.items()}

    # Strings/bytes should not be treated as iterables here
    if isinstance(obj, (str, bytes)):
        return _serialize_value(obj)

    # If user explicitly says many=True or obj is a list/tuple/set -> treat as collection
    if many is True or (many is None and isinstance(obj, (list, tuple, set))):
        iterable = list(obj)
        return [_serialize_model_instance(item, include_relationships=include_relationships) for item in iterable]

    # If it's an iterable (but not string/bytes/dict), default to treating as collection when many is None
    if many is None and isinstance(obj, Iterable):
        try:
            # Avoid treating SQLAlchemy result proxies incorrectly: inspect first element
            iterable = list(obj)
            # If empty, return empty list
            if not iterable:
                return []
            return [_serialize_model_instance(item, include_relationships=include_relationships) for item in iterable]
        except TypeError:
            # Not a real iterable, fallthrough to single-instance handling
            pass

    # Otherwise treat as single model instance or scalar
    # If it looks like a SQLAlchemy mapped object, serialize via mapper
    if hasattr(obj, "__class__") and not isinstance(obj, (int, float, bool)):
        try:
            return _serialize_model_instance(obj, include_relationships=include_relationships)
        except Exception:
            # Fallback: return string representation
            return _serialize_value(obj)

    # Fallback for other scalars
    return _serialize_value(obj)


# --- Response makers ---------------------------------------------------------
def success_response(
    data: Any = None, status: int = 200, meta: Optional[Dict[str, Any]] = None
) -> tuple:
    """
    Return a standardized success JSON response.

    Example payload:
    {
      "status": "success",
      "data": {...},
      "error": None,
      "meta": {...}
    }
    """
    payload = {"status": "success", "data": data, "error": None, "meta": meta or None}
    return jsonify(payload), status


def error_response(
    message: str = "Error",
    status: int = 400,
    code: Optional[str] = None,
    details: Optional[Dict[str, Any]] = None,
) -> tuple:
    """
    Return a standardized error JSON response.

    Args:
      - message: human-friendly message
      - status: HTTP status code
      - code: machine-friendly error code (optional)
      - details: optional structured details (avoid secrets)
    """
    error_payload = {"message": message}
    if code:
        error_payload["code"] = code
    if details:
        # sanitize details if necessary before sending
        error_payload["details"] = details

    payload = {"status": "error", "data": None, "error": error_payload, "meta": None}
    return jsonify(payload), int(status)
