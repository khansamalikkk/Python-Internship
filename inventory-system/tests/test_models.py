import pytest

from inventory_system.exceptions import ValidationError
from inventory_system.models import Category, Product


def test_category_valid():
    c = Category(id=1, name="Electronics", description="Gadgets")
    assert c.name == "Electronics"
    assert c.to_dict() == {"id": 1, "name": "Electronics", "description": "Gadgets"}


def test_category_empty_name_raises():
    with pytest.raises(ValidationError):
        Category(id=1, name="   ")


def test_category_from_dict_roundtrip():
    data = {"id": 2, "name": "Books", "description": "Reading material"}
    c = Category.from_dict(data)
    assert c.to_dict() == data


def test_product_valid_and_derived_properties():
    p = Product(sku="abc-1", name="Widget", category_id=1, price=9.999, quantity=3, reorder_level=5)
    assert p.sku == "ABC-1"  # normalized to uppercase
    assert p.price == 10.0  # rounded to 2dp
    assert p.total_value == 30.0
    assert p.is_low_stock is True  # quantity(3) <= reorder_level(5)


def test_product_not_low_stock():
    p = Product(sku="X1", name="Gizmo", category_id=1, price=5, quantity=100, reorder_level=5)
    assert p.is_low_stock is False


@pytest.mark.parametrize("bad_price", ["abc", None])
def test_product_invalid_price_raises(bad_price):
    with pytest.raises(ValidationError):
        Product(sku="X1", name="Gizmo", category_id=1, price=bad_price, quantity=1)


def test_product_negative_quantity_raises():
    with pytest.raises(ValidationError):
        Product(sku="X1", name="Gizmo", category_id=1, price=5, quantity=-1)


def test_product_empty_name_raises():
    with pytest.raises(ValidationError):
        Product(sku="X1", name="", category_id=1, price=5, quantity=1)


def test_product_from_dict_roundtrip():
    data = {
        "sku": "SKU1",
        "name": "Item",
        "category_id": 2,
        "price": 12.5,
        "quantity": 4,
        "reorder_level": 2,
        "description": "desc",
    }
    p = Product.from_dict(data)
    assert p.to_dict() == data
