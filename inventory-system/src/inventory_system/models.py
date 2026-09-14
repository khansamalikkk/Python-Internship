"""Domain models for the inventory system: Category and Product."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict

from .exceptions import ValidationError


def _require_non_empty_str(value: Any, field_name: str, max_len: int = 100) -> str:
    text = (str(value) if value is not None else "").strip()
    if not text:
        raise ValidationError(f"{field_name} cannot be empty.")
    if len(text) > max_len:
        raise ValidationError(f"{field_name} must be {max_len} characters or fewer.")
    return text


def _require_non_negative_number(value: Any, field_name: str) -> float:
    try:
        num = float(value)
    except (TypeError, ValueError):
        raise ValidationError(f"{field_name} must be a number.")
    if num < 0:
        raise ValidationError(f"{field_name} cannot be negative.")
    return num


def _require_non_negative_int(value: Any, field_name: str) -> int:
    try:
        num = int(value)
    except (TypeError, ValueError):
        raise ValidationError(f"{field_name} must be an integer.")
    if num < 0:
        raise ValidationError(f"{field_name} cannot be negative.")
    return num


@dataclass
class Category:
    """A product category, e.g. 'Electronics' or 'Stationery'."""

    id: int
    name: str
    description: str = ""

    def __post_init__(self) -> None:
        self.name = _require_non_empty_str(self.name, "Category name", max_len=50)
        self.description = (self.description or "").strip()[:200]

    def to_dict(self) -> Dict[str, Any]:
        return {"id": self.id, "name": self.name, "description": self.description}

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Category":
        return cls(id=int(data["id"]), name=data["name"], description=data.get("description", ""))


@dataclass
class Product:
    """A single product held in inventory."""

    sku: str
    name: str
    category_id: int
    price: float
    quantity: int
    reorder_level: int = 5
    description: str = ""

    def __post_init__(self) -> None:
        self.sku = _require_non_empty_str(self.sku, "SKU", max_len=30).upper()
        self.name = _require_non_empty_str(self.name, "Product name", max_len=100)
        self.price = round(_require_non_negative_number(self.price, "Price"), 2)
        self.quantity = _require_non_negative_int(self.quantity, "Quantity")
        self.reorder_level = _require_non_negative_int(self.reorder_level, "Reorder level")
        self.description = (self.description or "").strip()[:200]
        try:
            self.category_id = int(self.category_id)
        except (TypeError, ValueError):
            raise ValidationError("Category id must be an integer.")

    @property
    def total_value(self) -> float:
        """Total monetary value of stock on hand for this product."""
        return round(self.price * self.quantity, 2)

    @property
    def is_low_stock(self) -> bool:
        return self.quantity <= self.reorder_level

    def to_dict(self) -> Dict[str, Any]:
        return {
            "sku": self.sku,
            "name": self.name,
            "category_id": self.category_id,
            "price": self.price,
            "quantity": self.quantity,
            "reorder_level": self.reorder_level,
            "description": self.description,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Product":
        return cls(
            sku=data["sku"],
            name=data["name"],
            category_id=data["category_id"],
            price=data["price"],
            quantity=data["quantity"],
            reorder_level=data.get("reorder_level", 5),
            description=data.get("description", ""),
        )
