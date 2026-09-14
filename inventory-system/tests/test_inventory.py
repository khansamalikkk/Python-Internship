import json

import pytest

from inventory_system.exceptions import (
    CategoryNotFoundError,
    DuplicateCategoryError,
    DuplicateProductError,
    ProductNotFoundError,
    ValidationError,
)
from inventory_system.inventory import Inventory
from inventory_system.storage import JSONStorage


@pytest.fixture
def inv(tmp_path):
    data_file = tmp_path / "inventory_data.json"
    return Inventory(storage=JSONStorage(str(data_file)))


# ----------------------------------------------------------------------
# Categories
# ----------------------------------------------------------------------

def test_add_and_list_category(inv):
    cat = inv.add_category("Electronics", "Gadgets and devices")
    assert cat.id == 1
    assert inv.list_categories() == [cat]


def test_add_duplicate_category_raises(inv):
    inv.add_category("Electronics")
    with pytest.raises(DuplicateCategoryError):
        inv.add_category("electronics")  # case-insensitive duplicate check


def test_get_category_not_found(inv):
    with pytest.raises(CategoryNotFoundError):
        inv.get_category(999)


def test_remove_category_in_use_raises(inv):
    cat = inv.add_category("Electronics")
    inv.add_product(sku="A1", name="Phone", category_id=cat.id, price=100, quantity=5)
    with pytest.raises(ValidationError):
        inv.remove_category(cat.id)


def test_remove_category_success(inv):
    cat = inv.add_category("Empty Category")
    inv.remove_category(cat.id)
    assert inv.list_categories() == []


# ----------------------------------------------------------------------
# Products
# ----------------------------------------------------------------------

def test_add_product_requires_valid_category(inv):
    with pytest.raises(CategoryNotFoundError):
        inv.add_product(sku="A1", name="Phone", category_id=42, price=100, quantity=5)


def test_add_and_get_product(inv):
    cat = inv.add_category("Electronics")
    p = inv.add_product(sku="a1", name="Phone", category_id=cat.id, price=499.99, quantity=10)
    assert p.sku == "A1"
    fetched = inv.get_product("a1")
    assert fetched.name == "Phone"


def test_add_duplicate_product_raises(inv):
    cat = inv.add_category("Electronics")
    inv.add_product(sku="A1", name="Phone", category_id=cat.id, price=100, quantity=5)
    with pytest.raises(DuplicateProductError):
        inv.add_product(sku="a1", name="Phone 2", category_id=cat.id, price=150, quantity=3)


def test_get_missing_product_raises(inv):
    with pytest.raises(ProductNotFoundError):
        inv.get_product("NOPE")


def test_update_product(inv):
    cat = inv.add_category("Electronics")
    inv.add_product(sku="A1", name="Phone", category_id=cat.id, price=100, quantity=5)
    updated = inv.update_product("A1", quantity=20, price=120)
    assert updated.quantity == 20
    assert updated.price == 120


def test_update_product_unknown_field_raises(inv):
    cat = inv.add_category("Electronics")
    inv.add_product(sku="A1", name="Phone", category_id=cat.id, price=100, quantity=5)
    with pytest.raises(ValidationError):
        inv.update_product("A1", made_up_field=1)


def test_update_product_missing_raises(inv):
    with pytest.raises(ProductNotFoundError):
        inv.update_product("NOPE", quantity=1)


def test_remove_product(inv):
    cat = inv.add_category("Electronics")
    inv.add_product(sku="A1", name="Phone", category_id=cat.id, price=100, quantity=5)
    inv.remove_product("A1")
    with pytest.raises(ProductNotFoundError):
        inv.get_product("A1")


# ----------------------------------------------------------------------
# Search
# ----------------------------------------------------------------------

def test_search_by_keyword(inv):
    cat = inv.add_category("Electronics")
    inv.add_product(sku="A1", name="Smartphone", category_id=cat.id, price=500, quantity=5)
    inv.add_product(sku="A2", name="Laptop", category_id=cat.id, price=1000, quantity=2)
    results = inv.search_products(keyword="phone")
    assert [p.sku for p in results] == ["A1"]


def test_search_by_category(inv):
    cat1 = inv.add_category("Electronics")
    cat2 = inv.add_category("Books")
    inv.add_product(sku="A1", name="Laptop", category_id=cat1.id, price=1000, quantity=2)
    inv.add_product(sku="B1", name="Novel", category_id=cat2.id, price=15, quantity=30)
    results = inv.search_products(category_id=cat2.id)
    assert [p.sku for p in results] == ["B1"]


def test_search_low_stock_only(inv):
    cat = inv.add_category("Electronics")
    inv.add_product(sku="A1", name="Low", category_id=cat.id, price=1, quantity=1, reorder_level=5)
    inv.add_product(sku="A2", name="High", category_id=cat.id, price=1, quantity=99, reorder_level=5)
    results = inv.search_products(low_stock_only=True)
    assert [p.sku for p in results] == ["A1"]


# ----------------------------------------------------------------------
# Reporting
# ----------------------------------------------------------------------

def test_summary_report(inv):
    cat = inv.add_category("Electronics")
    inv.add_product(sku="A1", name="Phone", category_id=cat.id, price=100, quantity=5, reorder_level=10)
    inv.add_product(sku="A2", name="Laptop", category_id=cat.id, price=1000, quantity=20, reorder_level=5)

    report = inv.summary_report()
    assert report["total_products"] == 2
    assert report["total_items_in_stock"] == 25
    assert report["total_inventory_value"] == pytest.approx(100 * 5 + 1000 * 20)
    assert report["low_stock_count"] == 1
    assert report["low_stock_skus"] == ["A1"]
    assert report["by_category"]["Electronics"]["product_count"] == 2


# ----------------------------------------------------------------------
# Persistence
# ----------------------------------------------------------------------

def test_persistence_across_instances(tmp_path):
    data_file = tmp_path / "inventory_data.json"
    inv1 = Inventory(storage=JSONStorage(str(data_file)))
    cat = inv1.add_category("Electronics")
    inv1.add_product(sku="A1", name="Phone", category_id=cat.id, price=100, quantity=5)

    # A fresh Inventory instance pointed at the same file should see the data.
    inv2 = Inventory(storage=JSONStorage(str(data_file)))
    assert inv2.get_product("A1").name == "Phone"
    assert inv2.get_category(cat.id).name == "Electronics"


def test_corrupt_file_recovers_gracefully(tmp_path):
    data_file = tmp_path / "inventory_data.json"
    data_file.write_text("{not valid json", encoding="utf-8")

    inv_instance = Inventory(storage=JSONStorage(str(data_file)))
    assert inv_instance.list_products() == []
    assert inv_instance.list_categories() == []

    backups = list(tmp_path.glob("inventory_data.json.corrupt.*.bak"))
    assert len(backups) == 1
