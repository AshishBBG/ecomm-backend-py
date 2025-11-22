"""
Application-specific exceptions.

Each exception exposes:
- message: human-friendly error message
- status_code: HTTP status code to return
- code: short machine-friendly error code (useful for clients/logging)
- payload/details: optional dict with structured data (non-sensitive)

Usage:
    raise NotFoundError("User not found", details={"user_id": user_id})
"""

from typing import Any, Dict, Optional


class AppError(Exception):
    """Base application error with structured data for JSON responses."""

    default_message: str = "An application error occurred"
    default_status: int = 500
    default_code: str = "app_error"

    def __init__(
        self,
        message: Optional[str] = None,
        status_code: Optional[int] = None,
        code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        """
        Args:
            message: human readable message
            status_code: HTTP status code
            code: short machine friendly error code (snake_case)
            details: optional structured payload with extra non-sensitive information
        """
        super().__init__(message or self.default_message)
        self.message = message or self.default_message
        self.status_code = int(status_code or self.default_status)
        self.code = code or self.default_code
        self.details = details or {}

    def to_dict(self) -> Dict[str, Any]:
        """Return a JSON-serializable representation of the error."""
        payload = {"status": "error", "message": self.message, "code": self.code}
        if self.details:
            payload["details"] = self.details
        return payload

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} code={self.code} status={self.status_code} message={self.message!r}>"


# Common HTTP-like exceptions -------------------------------------------------


class BadRequestError(AppError):
    default_message = "Bad request"
    default_status = 400
    default_code = "bad_request"


class ValidationError(BadRequestError):
    default_message = "Validation failed"
    default_code = "validation_error"

    def __init__(self, message: Optional[str] = None, details: Optional[Dict[str, Any]] = None):
        # Validation errors usually return 400
        super().__init__(message=message, status_code=400, code=self.default_code, details=details)


class UnauthorizedError(AppError):
    default_message = "Unauthorized"
    default_status = 401
    default_code = "unauthorized"


class ForbiddenError(AppError):
    default_message = "Forbidden"
    default_status = 403
    default_code = "forbidden"


class NotFoundError(AppError):
    default_message = "Not found"
    default_status = 404
    default_code = "not_found"


class ConflictError(AppError):
    default_message = "Conflict"
    default_status = 409
    default_code = "conflict"


class ServiceError(AppError):
    """Generic service-level error (4xx by default in your original code used 400)."""
    default_message = "Service error"
    default_status = 400
    default_code = "service_error"
