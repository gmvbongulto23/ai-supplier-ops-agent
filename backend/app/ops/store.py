import uuid
from datetime import datetime, timedelta

from app.ops.models import (
    Delivery,
    Inventory,
    Order,
    OrderStatus,
    Recommendation,
    ReliabilityStatus,
    Supplier,
)

suppliers: dict[str, Supplier] = {}
orders: dict[str, Order] = {}
deliveries: dict[str, Delivery] = {}
inventory: dict[str, Inventory] = {}
recommendations: dict[str, Recommendation] = {}


def new_id() -> str:
    return uuid.uuid4().hex[:12]


SUPPLIER_MILK_PRIMARY = "supplier-milk-primary"
SUPPLIER_MILK_BACKUP = "supplier-milk-backup"
SUPPLIER_FLOUR_PRIMARY = "supplier-flour-primary"
SUPPLIER_FLOUR_BACKUP = "supplier-flour-backup"
ORDER_MILK = "order-milk"
ORDER_FLOUR = "order-flour"


def seed_baseline() -> None:
    """Reset all store state to the normal-day scenario (scenario 1)."""
    suppliers.clear()
    orders.clear()
    deliveries.clear()
    inventory.clear()
    recommendations.clear()

    now = datetime.utcnow()

    suppliers[SUPPLIER_MILK_PRIMARY] = Supplier(
        id=SUPPLIER_MILK_PRIMARY,
        name="Dairy Farms Co",
        products_supplied=["milk"],
        reliability_status=ReliabilityStatus.RELIABLE,
        contact_info="orders@dairyfarms.example",
    )
    suppliers[SUPPLIER_MILK_BACKUP] = Supplier(
        id=SUPPLIER_MILK_BACKUP,
        name="Valley Dairy Co-op",
        products_supplied=["milk"],
        reliability_status=ReliabilityStatus.RELIABLE,
        contact_info="orders@valleydairy.example",
    )
    suppliers[SUPPLIER_FLOUR_PRIMARY] = Supplier(
        id=SUPPLIER_FLOUR_PRIMARY,
        name="Grain Mills Inc",
        products_supplied=["flour"],
        reliability_status=ReliabilityStatus.RELIABLE,
        contact_info="orders@grainmills.example",
    )
    suppliers[SUPPLIER_FLOUR_BACKUP] = Supplier(
        id=SUPPLIER_FLOUR_BACKUP,
        name="Golden Wheat Suppliers",
        products_supplied=["flour"],
        reliability_status=ReliabilityStatus.INCONSISTENT,
        contact_info="orders@goldenwheat.example",
    )

    milk_expected = now + timedelta(hours=2)
    flour_expected = now + timedelta(hours=3)

    orders[ORDER_MILK] = Order(
        id=ORDER_MILK,
        supplier_id=SUPPLIER_MILK_PRIMARY,
        product="milk",
        quantity=200,
        order_date=now - timedelta(hours=2),
        expected_delivery=milk_expected,
        status=OrderStatus.ON_TIME,
    )
    orders[ORDER_FLOUR] = Order(
        id=ORDER_FLOUR,
        supplier_id=SUPPLIER_FLOUR_PRIMARY,
        product="flour",
        quantity=150,
        order_date=now - timedelta(hours=2),
        expected_delivery=flour_expected,
        status=OrderStatus.ON_TIME,
    )

    deliveries[ORDER_MILK] = Delivery(order_id=ORDER_MILK, eta=milk_expected, status=OrderStatus.ON_TIME)
    deliveries[ORDER_FLOUR] = Delivery(order_id=ORDER_FLOUR, eta=flour_expected, status=OrderStatus.ON_TIME)

    inventory["milk"] = Inventory(
        product="milk", current_quantity=40, avg_usage_per_hour=15, minimum_required_quantity=20
    )
    inventory["flour"] = Inventory(
        product="flour", current_quantity=100, avg_usage_per_hour=10, minimum_required_quantity=30
    )


def _delay_delivery(order_id: str, hours: float, reason: str) -> None:
    delivery = deliveries[order_id]
    delivery.eta = delivery.eta + timedelta(hours=hours)
    delivery.status = OrderStatus.DELAYED
    delivery.delay_info = f"{hours:g} hour delay - {reason}"
    orders[order_id].status = OrderStatus.DELAYED


SCENARIOS = {"normal", "supplier_delay", "multiple_delays", "inventory_shortage"}


def apply_scenario(name: str) -> None:
    if name not in SCENARIOS:
        raise ValueError(f"Unknown scenario '{name}'. Must be one of {sorted(SCENARIOS)}.")

    seed_baseline()

    if name == "normal":
        return

    if name == "supplier_delay":
        _delay_delivery(ORDER_MILK, 3, "traffic incident")
        return

    if name == "multiple_delays":
        _delay_delivery(ORDER_MILK, 3, "traffic incident")
        _delay_delivery(ORDER_FLOUR, 6, "mill equipment breakdown")
        inventory["flour"].current_quantity = 40
        inventory["flour"].avg_usage_per_hour = 12
        return

    if name == "inventory_shortage":
        inventory["flour"].current_quantity = 20
        return
