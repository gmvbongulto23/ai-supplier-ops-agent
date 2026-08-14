from fastapi import APIRouter, HTTPException

from app.ops import agent, logic, store
from app.ops.models import (
    Delivery,
    DeliveryCreate,
    Inventory,
    InventoryCreate,
    Order,
    OrderCreate,
    Recommendation,
    Supplier,
    SupplierCreate,
)

router = APIRouter(prefix="/ops", tags=["ops"])


@router.get("/suppliers", response_model=list[Supplier])
def list_suppliers() -> list[Supplier]:
    return list(store.suppliers.values())


@router.post("/suppliers", response_model=Supplier, status_code=201)
def create_supplier(payload: SupplierCreate) -> Supplier:
    supplier = Supplier(id=store.new_id(), **payload.model_dump())
    store.suppliers[supplier.id] = supplier
    return supplier


@router.get("/suppliers/{supplier_id}", response_model=Supplier)
def get_supplier(supplier_id: str) -> Supplier:
    supplier = store.suppliers.get(supplier_id)
    if supplier is None:
        raise HTTPException(status_code=404, detail="Supplier not found")
    return supplier


@router.get("/orders", response_model=list[Order])
def list_orders() -> list[Order]:
    return list(store.orders.values())


@router.post("/orders", response_model=Order, status_code=201)
def create_order(payload: OrderCreate) -> Order:
    if payload.supplier_id not in store.suppliers:
        raise HTTPException(status_code=422, detail="Unknown supplier_id")
    order = Order(id=store.new_id(), **payload.model_dump())
    store.orders[order.id] = order
    return order


@router.get("/orders/{order_id}", response_model=Order)
def get_order(order_id: str) -> Order:
    order = store.orders.get(order_id)
    if order is None:
        raise HTTPException(status_code=404, detail="Order not found")
    return order


@router.get("/deliveries", response_model=list[Delivery])
def list_deliveries() -> list[Delivery]:
    return list(store.deliveries.values())


@router.post("/deliveries", response_model=Delivery, status_code=201)
def create_delivery(payload: DeliveryCreate) -> Delivery:
    if payload.order_id not in store.orders:
        raise HTTPException(status_code=422, detail="Unknown order_id")
    delivery = Delivery(**payload.model_dump())
    store.deliveries[delivery.order_id] = delivery
    return delivery


@router.get("/inventory", response_model=list[Inventory])
def list_inventory() -> list[Inventory]:
    return list(store.inventory.values())


@router.post("/inventory", response_model=Inventory, status_code=201)
def create_inventory(payload: InventoryCreate) -> Inventory:
    item = Inventory(**payload.model_dump())
    store.inventory[item.product] = item
    return item


@router.get("/recommendations", response_model=list[Recommendation])
def list_recommendations() -> list[Recommendation]:
    return sorted(store.recommendations.values(), key=lambda r: r.created_at, reverse=True)


@router.post("/recommendations/{recommendation_id}/accept", response_model=Recommendation)
def accept_recommendation(recommendation_id: str) -> Recommendation:
    try:
        return agent.accept_recommendation(recommendation_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="Recommendation not found") from exc


@router.post("/scenarios/{name}/trigger", response_model=list[Recommendation])
def trigger_scenario(name: str) -> list[Recommendation]:
    try:
        store.apply_scenario(name)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    return agent.run_agent_cycle()


@router.get("/dashboard")
def get_dashboard() -> dict:
    delivery_counts: dict[str, int] = {}
    for order in store.orders.values():
        delivery_counts[order.status.value] = delivery_counts.get(order.status.value, 0) + 1

    pending_products = {r.product for r in store.recommendations.values() if r.status.value == "pending"}

    inventory_view = []
    for item in store.inventory.values():
        below_minimum = logic.is_below_minimum(item)
        status = "critical" if below_minimum else ("at_risk" if item.product in pending_products else "healthy")
        inventory_view.append(
            {
                "product": item.product,
                "current_quantity": item.current_quantity,
                "avg_usage_per_hour": item.avg_usage_per_hour,
                "minimum_required_quantity": item.minimum_required_quantity,
                "estimated_remaining_hours": round(logic.estimate_remaining_supply(item), 1),
                "status": status,
            }
        )

    orders_view = []
    for order in store.orders.values():
        supplier = store.suppliers.get(order.supplier_id)
        delivery = store.deliveries.get(order.id)
        orders_view.append(
            {
                "id": order.id,
                "supplier_name": supplier.name if supplier else "Unknown",
                "product": order.product,
                "quantity": order.quantity,
                "expected_delivery": order.expected_delivery,
                "current_eta": delivery.eta if delivery else order.expected_delivery,
                "status": order.status.value,
                "delay_info": delivery.delay_info if delivery else None,
            }
        )

    return {
        "delivery_summary": delivery_counts,
        "inventory": inventory_view,
        "orders": orders_view,
        "recommendations": [r.model_dump() for r in list_recommendations()],
    }
