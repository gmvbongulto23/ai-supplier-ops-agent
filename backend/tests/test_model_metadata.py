import uuid

from sqlalchemy import CheckConstraint, DateTime
from sqlalchemy.dialects.postgresql import UUID

import app.models  # noqa: F401  (registers all tables on Base.metadata)
from app.db.base import Base
from app.models.enums import OrderStatus, SupplierReliability

TABLES = Base.metadata.tables


def _check_constraint_texts(table_name: str) -> list[str]:
    table = TABLES[table_name]
    return [str(c.sqltext) for c in table.constraints if isinstance(c, CheckConstraint)]


def _index_names(table_name: str) -> set[str]:
    return {index.name for index in TABLES[table_name].indexes}


def test_expected_tables_are_registered():
    assert set(TABLES.keys()) == {"suppliers", "products", "orders", "deliveries", "inventory"}


def test_every_table_has_a_uuid_primary_key():
    for table_name, table in TABLES.items():
        pk_columns = list(table.primary_key.columns)
        assert len(pk_columns) == 1, f"{table_name} should have exactly one primary key column"
        pk_column = pk_columns[0]
        assert pk_column.name == "id"
        assert isinstance(pk_column.type, UUID)
        assert pk_column.default is not None
        # SQLAlchemy wraps callable defaults in a (ctx)-accepting shim; __wrapped__ is the original callable
        assert pk_column.default.arg.__wrapped__ is uuid.uuid4


def test_every_table_has_created_and_updated_timestamps_with_defaults():
    for table_name, table in TABLES.items():
        for column_name in ("created_at", "updated_at"):
            column = table.columns[column_name]
            assert isinstance(column.type, DateTime)
            assert column.type.timezone is True
            assert column.nullable is False
            assert column.server_default is not None, f"{table_name}.{column_name} needs a server_default"
        assert table.columns["updated_at"].onupdate is not None


def test_supplier_reliability_is_constrained_to_the_locked_vocabulary():
    column = TABLES["suppliers"].columns["reliability"]
    assert column.nullable is False
    assert column.type.name == "supplier_reliability"
    assert column.type.enum_class is SupplierReliability
    assert set(column.type.enums) == {"reliable", "inconsistent"}


def test_order_and_delivery_status_share_the_locked_order_status_vocabulary():
    order_status_column = TABLES["orders"].columns["status"]
    delivery_status_column = TABLES["deliveries"].columns["status"]

    for column in (order_status_column, delivery_status_column):
        assert column.nullable is False
        assert column.type.name == "order_status"
        assert column.type.enum_class is OrderStatus
        assert set(column.type.enums) == {"on_time", "delayed", "at_risk", "delivered"}


def test_orders_quantity_has_a_non_negative_check_constraint():
    assert "quantity >= 0" in _check_constraint_texts("orders")


def test_inventory_quantities_have_non_negative_check_constraints():
    constraints = _check_constraint_texts("inventory")
    assert "quantity_on_hand >= 0" in constraints
    assert "safety_stock >= 0" in constraints


def test_orders_foreign_keys_reference_suppliers_and_products():
    orders = TABLES["orders"]
    fk_targets = {fk.column.table.name: fk.column.name for fk in orders.foreign_keys}
    assert fk_targets == {"suppliers": "id", "products": "id"}


def test_deliveries_foreign_key_references_orders():
    deliveries = TABLES["deliveries"]
    fk_targets = {fk.column.table.name: fk.column.name for fk in deliveries.foreign_keys}
    assert fk_targets == {"orders": "id"}


def test_inventory_foreign_key_references_products():
    inventory = TABLES["inventory"]
    fk_targets = {fk.column.table.name: fk.column.name for fk in inventory.foreign_keys}
    assert fk_targets == {"products": "id"}


def test_foreign_key_and_dashboard_query_indexes_are_present():
    assert "ix_suppliers_reliability" in _index_names("suppliers")

    order_indexes = _index_names("orders")
    assert {"ix_orders_supplier_id", "ix_orders_product_id", "ix_orders_status", "ix_orders_supplier_status"} <= order_indexes

    delivery_indexes = _index_names("deliveries")
    assert {"ix_deliveries_order_id", "ix_deliveries_status", "ix_deliveries_order_status"} <= delivery_indexes

    assert "ix_inventory_product_id" in _index_names("inventory")


def test_inventory_has_a_unique_constraint_on_product_and_location():
    inventory = TABLES["inventory"]
    unique_constraints = [tuple(c.name for c in uc.columns) for uc in inventory.constraints if hasattr(uc, "columns") and getattr(uc, "name", None) == "uq_inventory_product_location"]
    assert ("product_id", "location") in unique_constraints
