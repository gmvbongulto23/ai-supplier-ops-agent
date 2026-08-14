import json
import os
import uuid
from datetime import date
from pathlib import Path

import pytest
from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.exc import DataError, IntegrityError
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.models import Delivery, Inventory, Order, Product, Supplier
from app.models.enums import SupplierReliability

BACKEND_DIR = Path(__file__).resolve().parent.parent
FIXTURES_PATH = Path(__file__).resolve().parent / "fixtures" / "operational_seed.json"
TEST_DATABASE_URL = os.environ.get("TEST_DATABASE_URL", "postgresql://localhost:5432/supply_chain_ops_test")
OPERATIONAL_TABLES = {"suppliers", "products", "orders", "deliveries", "inventory"}


@pytest.fixture(scope="module", autouse=True)
def _use_test_database():
    previous = os.environ.get("APP_DATABASE_URL")
    os.environ["APP_DATABASE_URL"] = TEST_DATABASE_URL
    get_settings.cache_clear()
    yield
    if previous is None:
        os.environ.pop("APP_DATABASE_URL", None)
    else:
        os.environ["APP_DATABASE_URL"] = previous
    get_settings.cache_clear()


@pytest.fixture(scope="module")
def alembic_config():
    return Config(str(BACKEND_DIR / "alembic.ini"))


@pytest.fixture(scope="module")
def engine():
    sync_url = TEST_DATABASE_URL.replace("postgresql://", "postgresql+psycopg://", 1)
    eng = create_engine(sync_url, future=True)
    yield eng
    eng.dispose()


@pytest.fixture(scope="module")
def migrated_schema(alembic_config, engine):
    command.upgrade(alembic_config, "head")
    yield
    command.downgrade(alembic_config, "base")


@pytest.fixture()
def db_session(migrated_schema, engine):
    connection = engine.connect()
    session = Session(bind=connection)
    yield session
    session.close()
    connection.execute(text("TRUNCATE TABLE deliveries, inventory, orders, products, suppliers RESTART IDENTITY CASCADE"))
    connection.commit()
    connection.close()


@pytest.fixture()
def seed_data():
    return json.loads(FIXTURES_PATH.read_text())


@pytest.fixture()
def seeded_supplier_and_product(db_session):
    supplier_id = uuid.uuid4()
    product_id = uuid.uuid4()
    db_session.execute(
        text("INSERT INTO suppliers (id, name, reliability) VALUES (:id, :name, :reliability)"),
        {"id": supplier_id, "name": "Fixture Supplier", "reliability": "reliable"},
    )
    db_session.execute(
        text("INSERT INTO products (id, sku, name) VALUES (:id, :sku, :name)"),
        {"id": product_id, "sku": "SKU-FIXTURE", "name": "Fixture Product"},
    )
    db_session.commit()
    return supplier_id, product_id


def test_migration_creates_expected_tables(migrated_schema, engine):
    inspector = inspect(engine)
    assert set(inspector.get_table_names()) - {"alembic_version"} == OPERATIONAL_TABLES


def test_migration_downgrade_removes_tables_and_reupgrade_restores_them(alembic_config, engine, migrated_schema):
    command.downgrade(alembic_config, "base")
    inspector = inspect(engine)
    assert set(inspector.get_table_names()) - {"alembic_version"} == set()

    command.upgrade(alembic_config, "head")
    inspector = inspect(engine)
    assert set(inspector.get_table_names()) - {"alembic_version"} == OPERATIONAL_TABLES


def test_valid_operational_seed_inserts_successfully(db_session, seed_data):
    for row in seed_data["suppliers"]:
        db_session.add(Supplier(id=uuid.UUID(row["id"]), name=row["name"], reliability=row["reliability"]))
    for row in seed_data["products"]:
        db_session.add(Product(id=uuid.UUID(row["id"]), sku=row["sku"], name=row["name"]))
    db_session.flush()

    for row in seed_data["orders"]:
        db_session.add(
            Order(
                id=uuid.UUID(row["id"]),
                supplier_id=uuid.UUID(row["supplier_id"]),
                product_id=uuid.UUID(row["product_id"]),
                status=row["status"],
                quantity=row["quantity"],
            )
        )
    db_session.flush()

    for row in seed_data["deliveries"]:
        db_session.add(
            Delivery(
                id=uuid.UUID(row["id"]),
                order_id=uuid.UUID(row["order_id"]),
                status=row["status"],
                expected_date=date.fromisoformat(row["expected_date"]),
                actual_date=date.fromisoformat(row["actual_date"]) if row["actual_date"] else None,
            )
        )
    for row in seed_data["inventory"]:
        db_session.add(
            Inventory(
                id=uuid.UUID(row["id"]),
                product_id=uuid.UUID(row["product_id"]),
                location=row["location"],
                quantity_on_hand=row["quantity_on_hand"],
                safety_stock=row["safety_stock"],
            )
        )
    db_session.commit()

    assert db_session.query(Supplier).count() == 2
    assert db_session.query(Product).count() == 1
    assert db_session.query(Order).count() == 1
    assert db_session.query(Delivery).count() == 1
    assert db_session.query(Inventory).count() == 1

    reliable_supplier = db_session.get(Supplier, uuid.UUID(seed_data["suppliers"][0]["id"]))
    assert reliable_supplier.reliability == SupplierReliability.RELIABLE
    assert reliable_supplier.created_at is not None
    assert reliable_supplier.updated_at is not None


def test_invalid_supplier_reliability_is_rejected_by_the_database(db_session):
    with pytest.raises(DataError):
        db_session.execute(
            text("INSERT INTO suppliers (id, name, reliability) VALUES (:id, :name, :reliability)"),
            {"id": uuid.uuid4(), "name": "Bad Supplier Co", "reliability": "unknown"},
        )
    db_session.rollback()


def test_invalid_order_status_is_rejected_by_the_database(db_session, seeded_supplier_and_product):
    supplier_id, product_id = seeded_supplier_and_product
    with pytest.raises(DataError):
        db_session.execute(
            text(
                "INSERT INTO orders (id, supplier_id, product_id, status, quantity) "
                "VALUES (:id, :supplier_id, :product_id, :status, :quantity)"
            ),
            {"id": uuid.uuid4(), "supplier_id": supplier_id, "product_id": product_id, "status": "lost", "quantity": 5},
        )
    db_session.rollback()


def test_order_rejects_missing_supplier_or_product(db_session):
    with pytest.raises(IntegrityError):
        db_session.execute(
            text(
                "INSERT INTO orders (id, supplier_id, product_id, status, quantity) "
                "VALUES (:id, :supplier_id, :product_id, :status, :quantity)"
            ),
            {"id": uuid.uuid4(), "supplier_id": uuid.uuid4(), "product_id": uuid.uuid4(), "status": "on_time", "quantity": 5},
        )
    db_session.rollback()


def test_delivery_rejects_missing_order(db_session):
    with pytest.raises(IntegrityError):
        db_session.execute(
            text("INSERT INTO deliveries (id, order_id, status, expected_date) VALUES (:id, :order_id, :status, :expected_date)"),
            {"id": uuid.uuid4(), "order_id": uuid.uuid4(), "status": "on_time", "expected_date": date(2026, 1, 1)},
        )
    db_session.rollback()


def test_order_rejects_negative_quantity(db_session, seeded_supplier_and_product):
    supplier_id, product_id = seeded_supplier_and_product
    with pytest.raises(IntegrityError):
        db_session.execute(
            text(
                "INSERT INTO orders (id, supplier_id, product_id, status, quantity) "
                "VALUES (:id, :supplier_id, :product_id, :status, :quantity)"
            ),
            {"id": uuid.uuid4(), "supplier_id": supplier_id, "product_id": product_id, "status": "on_time", "quantity": -10},
        )
    db_session.rollback()


def test_inventory_rejects_negative_quantity_on_hand(db_session, seeded_supplier_and_product):
    _, product_id = seeded_supplier_and_product
    with pytest.raises(IntegrityError):
        db_session.execute(
            text(
                "INSERT INTO inventory (id, product_id, location, quantity_on_hand, safety_stock) "
                "VALUES (:id, :product_id, :location, :qty, :safety)"
            ),
            {"id": uuid.uuid4(), "product_id": product_id, "location": "Warehouse-X", "qty": -1, "safety": 0},
        )
    db_session.rollback()


def test_inventory_rejects_negative_safety_stock(db_session, seeded_supplier_and_product):
    _, product_id = seeded_supplier_and_product
    with pytest.raises(IntegrityError):
        db_session.execute(
            text(
                "INSERT INTO inventory (id, product_id, location, quantity_on_hand, safety_stock) "
                "VALUES (:id, :product_id, :location, :qty, :safety)"
            ),
            {"id": uuid.uuid4(), "product_id": product_id, "location": "Warehouse-X", "qty": 10, "safety": -5},
        )
    db_session.rollback()
