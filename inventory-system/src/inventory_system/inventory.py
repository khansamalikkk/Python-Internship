"""Core Inventory class: manages categories and products, with CRUD
operations, search, persistence, and summary reporting."""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from .exceptions import (
    CategoryNotFoundError,
    DuplicateCategoryError,
    DuplicateProductError,
    ProductNotFoundError,
    ValidationError,
)
from .models import Category, Product
from .storage import JSONStorage


class Inventory:
    """In-memory inventory of categories and products, backed by JSON storage.

    Categories and products are kept in dictionaries keyed by id/SKU for
    O(1) lookup, update, and removal.
    """

    def __init__(self, storage: Optional[JSONStorage] = None):
        self.storage = storage or JSONStorage()
        self._categories: Dict[int, Category] = {}
        self._products: Dict[str, Product] = {}
        self._next_category_id = 1
        self.load()

    # ------------------------------------------------------------------
    # Persistence
    # ------------------------------------------------------------------
    def load(self) -> None:
        data = self.storage.load()
        self._categories = {
            c["id"]: Category.from_dict(c) for c in data.get("categories", [])
        }
        self._products = {
            p["sku"]: Product.from_dict(p) for p in data.get("products", [])
        }
        self._next_category_id = (max(self._categories.keys(), default=0)) + 1

    def save(self) -> None:
        data = {
            "categories": [c.to_dict() for c in self._categories.values()],
            "products": [p.to_dict() for p in self._products.values()],
        }
        self.storage.save(data)

    # ------------------------------------------------------------------
    # Category operations
    # ------------------------------------------------------------------
    def add_category(self, name: str, description: str = "") -> Category:
        name_clean = (name or "").strip()
        if any(c.name.lower() == name_clean.lower() for c in self._categories.values()):
            raise DuplicateCategoryError(f"Category '{name_clean}' already exists.")
        category = Category(id=self._next_category_id, name=name, description=description)
        self._categories[category.id] = category
        self._next_category_id += 1
        self.save()
        return category

    def get_category(self, category_id: int) -> Category:
        try:
            return self._categories[int(category_id)]
        except (KeyError, TypeError, ValueError):
            raise CategoryNotFoundError(f"Category id {category_id} not found.")

    def list_categories(self) -> List[Category]:
        return sorted(self._categories.values(), key=lambda c: c.id)

    def remove_category(self, category_id: int) -> None:
        category = self.get_category(category_id)  # raises if not found
        in_use = [p for p in self._products.values() if p.category_id == category.id]
        if in_use:
            raise ValidationError(
                f"Cannot remove category '{category.name}': "
                f"{len(in_use)} product(s) still assigned to it."
            )
        del self._categories[category.id]
        self.save()

    # ------------------------------------------------------------------
    # Product operations
    # ------------------------------------------------------------------
    def add_product(
        self,
        sku: str,
        name: str,
        category_id: int,
        price: float,
        quantity: int,
        reorder_level: int = 5,
        description: str = "",
    ) -> Product:
        # Validate category exists before creating the product.
        self.get_category(category_id)

        product = Product(
            sku=sku,
            name=name,
            category_id=category_id,
            price=price,
            quantity=quantity,
            reorder_level=reorder_level,
            description=description,
        )
        if product.sku in self._products:
            raise DuplicateProductError(f"Product with SKU '{product.sku}' already exists.")
        self._products[product.sku] = product
        self.save()
        return product

    def get_product(self, sku: str) -> Product:
        key = (sku or "").strip().upper()
        try:
            return self._products[key]
        except KeyError:
            raise ProductNotFoundError(f"Product with SKU '{sku}' not found.")

    def update_product(self, sku: str, **fields: Any) -> Product:
        existing = self.get_product(sku)  # raises if not found
        merged = existing.to_dict()

        allowed = {"name", "category_id", "price", "quantity", "reorder_level", "description"}
        unknown = set(fields) - allowed
        if unknown:
            raise ValidationError(f"Unknown field(s) for update: {sorted(unknown)}")

        for key, value in fields.items():
            if value is not None:
                merged[key] = value

        if "category_id" in fields and fields["category_id"] is not None:
            self.get_category(merged["category_id"])  # validate new category exists

        updated = Product.from_dict(merged)
        self._products[updated.sku] = updated
        self.save()
        return updated

    def remove_product(self, sku: str) -> None:
        product = self.get_product(sku)  # raises if not found
        del self._products[product.sku]
        self.save()

    def list_products(self) -> List[Product]:
        return sorted(self._products.values(), key=lambda p: p.sku)

    def search_products(
        self,
        keyword: Optional[str] = None,
        category_id: Optional[int] = None,
        low_stock_only: bool = False,
    ) -> List[Product]:
        results = list(self._products.values())

        if keyword:
            kw = keyword.strip().lower()
            results = [
                p for p in results
                if kw in p.name.lower() or kw in p.sku.lower() or kw in p.description.lower()
            ]

        if category_id is not None:
            results = [p for p in results if p.category_id == int(category_id)]

        if low_stock_only:
            results = [p for p in results if p.is_low_stock]

        return sorted(results, key=lambda p: p.sku)

    # ------------------------------------------------------------------
    # Reporting
    # ------------------------------------------------------------------
    def summary_report(self) -> Dict[str, Any]:
        products = self.list_products()
        total_items = sum(p.quantity for p in products)
        total_value = round(sum(p.total_value for p in products), 2)
        low_stock = [p for p in products if p.is_low_stock]

        by_category: Dict[str, Dict[str, Any]] = {}
        for category in self.list_categories():
            cat_products = [p for p in products if p.category_id == category.id]
            by_category[category.name] = {
                "product_count": len(cat_products),
                "total_quantity": sum(p.quantity for p in cat_products),
                "total_value": round(sum(p.total_value for p in cat_products), 2),
            }

        return {
            "total_products": len(products),
            "total_items_in_stock": total_items,
            "total_inventory_value": total_value,
            "low_stock_count": len(low_stock),
            "low_stock_skus": [p.sku for p in low_stock],
            "by_category": by_category,
        }
