from datetime import datetime

from app.ops import store
from app.ops.models import Delivery, Inventory, Order, OrderStatus, ReliabilityStatus, Supplier


def estimate_remaining_supply(item: Inventory) -> float:
    """Hours of supply remaining at the current usage rate."""
    if item.avg_usage_per_hour <= 0:
        return float("inf")
    return item.current_quantity / item.avg_usage_per_hour


def check_delivery_status(order: Order, delivery: Delivery) -> OrderStatus:
    """Compares the delivery's current ETA against the order's expected delivery time."""
    return OrderStatus.DELAYED if delivery.eta > order.expected_delivery else OrderStatus.ON_TIME


def hours_until(eta: datetime, *, now: datetime | None = None) -> float:
    now = now or datetime.utcnow()
    return max((eta - now).total_seconds() / 3600, 0)


def detect_shortage_risk(item: Inventory, delivery: Delivery, *, now: datetime | None = None) -> bool:
    """True when supply will run out before the (possibly delayed) delivery arrives."""
    remaining_hours = estimate_remaining_supply(item)
    time_until_delivery = hours_until(delivery.eta, now=now)
    return remaining_hours < time_until_delivery


def is_below_minimum(item: Inventory) -> bool:
    """True when current stock has already fallen below the required minimum."""
    return item.current_quantity < item.minimum_required_quantity


def find_backup_supplier(product: str, exclude_supplier_id: str | None = None) -> Supplier | None:
    """Looks up other suppliers who supply the same product, preferring reliable ones."""
    candidates = [
        supplier
        for supplier in store.suppliers.values()
        if product in supplier.products_supplied and supplier.id != exclude_supplier_id
    ]
    if not candidates:
        return None
    candidates.sort(key=lambda supplier: 0 if supplier.reliability_status == ReliabilityStatus.RELIABLE else 1)
    return candidates[0]
