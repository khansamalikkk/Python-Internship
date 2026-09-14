"""Custom exceptions for the inventory system."""


class InventoryError(Exception):
    """Base class for all inventory-related errors."""


class ValidationError(InventoryError):
    """Raised when user-supplied data fails validation."""


class ProductNotFoundError(InventoryError):
    """Raised when a product lookup by SKU/id fails."""


class CategoryNotFoundError(InventoryError):
    """Raised when a category lookup by id fails."""


class DuplicateProductError(InventoryError):
    """Raised when attempting to add a product with a SKU that already exists."""


class DuplicateCategoryError(InventoryError):
    """Raised when attempting to add a category with a name that already exists."""


class StorageError(InventoryError):
    """Raised when persistence (load/save) operations fail."""
