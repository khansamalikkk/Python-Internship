#!/usr/bin/env python3
"""Command-line interface for the Object-Oriented Inventory System.

Usage examples
--------------
    python -m inventory_system.cli add-category --name Electronics
    python -m inventory_system.cli add-product --sku LP-001 --name "Laptop" \\
        --category-id 1 --price 999.99 --quantity 10 --reorder-level 3
    python -m inventory_system.cli list-products
    python -m inventory_system.cli search --keyword laptop
    python -m inventory_system.cli update-product --sku LP-001 --quantity 25
    python -m inventory_system.cli remove-product --sku LP-001
    python -m inventory_system.cli report
"""

from __future__ import annotations

import argparse
import sys
from typing import List, Optional

from .exceptions import InventoryError
from .inventory import Inventory
from .storage import DEFAULT_DATA_FILE, JSONStorage


def _print_product_table(products) -> None:
    if not products:
        print("No matching products found.")
        return
    header = f"{'SKU':<10} {'Name':<25} {'Cat':<5} {'Price':>10} {'Qty':>6} {'Reorder':>8}  Low?"
    print(header)
    print("-" * len(header))
    for p in products:
        flag = "YES" if p.is_low_stock else ""
        print(
            f"{p.sku:<10} {p.name:<25.25} {p.category_id:<5} "
            f"{p.price:>10.2f} {p.quantity:>6} {p.reorder_level:>8}  {flag}"
        )


def cmd_add_category(args, inv: Inventory) -> int:
    category = inv.add_category(args.name, args.description)
    print(f"Added category #{category.id}: {category.name}")
    return 0


def cmd_list_categories(args, inv: Inventory) -> int:
    categories = inv.list_categories()
    if not categories:
        print("No categories defined yet.")
        return 0
    for c in categories:
        print(f"  [{c.id}] {c.name} - {c.description or '(no description)'}")
    return 0


def cmd_remove_category(args, inv: Inventory) -> int:
    inv.remove_category(args.id)
    print(f"Removed category #{args.id}.")
    return 0


def cmd_add_product(args, inv: Inventory) -> int:
    product = inv.add_product(
        sku=args.sku,
        name=args.name,
        category_id=args.category_id,
        price=args.price,
        quantity=args.quantity,
        reorder_level=args.reorder_level,
        description=args.description,
    )
    print(f"Added product {product.sku}: {product.name} (qty {product.quantity})")
    return 0


def cmd_update_product(args, inv: Inventory) -> int:
    updated = inv.update_product(
        args.sku,
        name=args.name,
        category_id=args.category_id,
        price=args.price,
        quantity=args.quantity,
        reorder_level=args.reorder_level,
        description=args.description,
    )
    print(f"Updated product {updated.sku}: {updated.name} (qty {updated.quantity})")
    return 0


def cmd_remove_product(args, inv: Inventory) -> int:
    inv.remove_product(args.sku)
    print(f"Removed product {args.sku}.")
    return 0


def cmd_list_products(args, inv: Inventory) -> int:
    _print_product_table(inv.list_products())
    return 0


def cmd_search(args, inv: Inventory) -> int:
    results = inv.search_products(
        keyword=args.keyword,
        category_id=args.category_id,
        low_stock_only=args.low_stock,
    )
    _print_product_table(results)
    print(f"\n{len(results)} match(es).")
    return 0


def cmd_report(args, inv: Inventory) -> int:
    report = inv.summary_report()
    print("Inventory Summary Report")
    print("=========================")
    print(f"Total distinct products : {report['total_products']}")
    print(f"Total items in stock    : {report['total_items_in_stock']}")
    print(f"Total inventory value   : {report['total_inventory_value']:.2f}")
    print(f"Low stock products      : {report['low_stock_count']}")
    if report["low_stock_skus"]:
        print(f"  SKUs: {', '.join(report['low_stock_skus'])}")

    print("\nBy category:")
    if not report["by_category"]:
        print("  (no categories defined)")
    for name, stats in report["by_category"].items():
        print(
            f"  {name:<20} products={stats['product_count']:<4} "
            f"qty={stats['total_quantity']:<6} value={stats['total_value']:.2f}"
        )
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="inventory_system",
        description="Object-Oriented Inventory Management CLI",
    )
    parser.add_argument(
        "--file", dest="data_file", default=DEFAULT_DATA_FILE,
        help=f"Path to the JSON data file (default: {DEFAULT_DATA_FILE})",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("add-category", help="Add a new category")
    p.add_argument("--name", required=True)
    p.add_argument("--description", default="")
    p.set_defaults(func=cmd_add_category)

    p = sub.add_parser("list-categories", help="List all categories")
    p.set_defaults(func=cmd_list_categories)

    p = sub.add_parser("remove-category", help="Remove a category by id")
    p.add_argument("--id", required=True, type=int)
    p.set_defaults(func=cmd_remove_category)

    p = sub.add_parser("add-product", help="Add a new product")
    p.add_argument("--sku", required=True)
    p.add_argument("--name", required=True)
    p.add_argument("--category-id", required=True, type=int, dest="category_id")
    p.add_argument("--price", required=True, type=float)
    p.add_argument("--quantity", required=True, type=int)
    p.add_argument("--reorder-level", type=int, default=5, dest="reorder_level")
    p.add_argument("--description", default="")
    p.set_defaults(func=cmd_add_product)

    p = sub.add_parser("update-product", help="Update fields of an existing product")
    p.add_argument("--sku", required=True)
    p.add_argument("--name", default=None)
    p.add_argument("--category-id", type=int, default=None, dest="category_id")
    p.add_argument("--price", type=float, default=None)
    p.add_argument("--quantity", type=int, default=None)
    p.add_argument("--reorder-level", type=int, default=None, dest="reorder_level")
    p.add_argument("--description", default=None)
    p.set_defaults(func=cmd_update_product)

    p = sub.add_parser("remove-product", help="Remove a product by SKU")
    p.add_argument("--sku", required=True)
    p.set_defaults(func=cmd_remove_product)

    p = sub.add_parser("list-products", help="List all products")
    p.set_defaults(func=cmd_list_products)

    p = sub.add_parser("search", help="Search products by keyword/category/low-stock")
    p.add_argument("--keyword", default=None)
    p.add_argument("--category-id", type=int, default=None, dest="category_id")
    p.add_argument("--low-stock", action="store_true", dest="low_stock")
    p.set_defaults(func=cmd_search)

    p = sub.add_parser("report", help="Show summary report")
    p.set_defaults(func=cmd_report)

    return parser


def main(argv: Optional[List[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    inv = Inventory(storage=JSONStorage(args.data_file))
    try:
        return args.func(args, inv)
    except InventoryError as exc:
        print(f"[Error] {exc}")
        return 1
    except Exception as exc:  # noqa: BLE001 - top-level safety net for a CLI tool
        print(f"[Fatal Error] An unexpected error occurred: {exc}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
