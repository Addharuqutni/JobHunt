"""
Custom exception classes for the application.
Provides domain-specific errors that are framework-agnostic.
"""


class AppException(Exception):
    """Base application exception."""

    def __init__(self, message: str, code: str = "UNKNOWN_ERROR"):
        self.message = message
        self.code = code
        super().__init__(self.message)


class EntityNotFoundError(AppException):
    """Raised when a requested entity does not exist."""

    def __init__(self, entity_name: str, identifier: str):
        super().__init__(
            message=f"{entity_name} with identifier '{identifier}' not found.",
            code="ENTITY_NOT_FOUND"
        )


class DuplicateEntityError(AppException):
    """Raised when attempting to create an entity that already exists."""

    def __init__(self, entity_name: str, field: str, value: str):
        super().__init__(
            message=f"{entity_name} with {field}='{value}' already exists.",
            code="DUPLICATE_ENTITY"
        )


class ValidationError(AppException):
    """Raised when input data fails domain validation."""

    def __init__(self, message: str):
        super().__init__(message=message, code="VALIDATION_ERROR")


class ScraperBusyError(AppException):
    """Raised when the scraper pipeline is already running."""

    def __init__(self):
        super().__init__(
            message="Scraper pipeline is already running. Please wait.",
            code="SCRAPER_BUSY"
        )
