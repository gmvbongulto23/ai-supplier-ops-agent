from datetime import datetime

from app.ops import logic, store
from app.ops.models import OrderStatus, Recommendation, RecommendationStatus

SEVERITY_RANK = {"critical": 0, "high": 1}


def run_agent_cycle() -> list[Recommendation]:
    """Monitor -> Detect -> Analyze -> Recommend across every order and inventory position."""
    new_recommendations: list[Recommendation] = []

    for order in store.orders.values():
        delivery = store.deliveries.get(order.id)
        item = store.inventory.get(order.product)
        if delivery is None or item is None:
            continue

        order.status = logic.check_delivery_status(order, delivery)
        if order.status != OrderStatus.DELAYED:
            continue

        if not logic.detect_shortage_risk(item, delivery):
            continue

        order.status = OrderStatus.AT_RISK
        remaining_hours = logic.estimate_remaining_supply(item)
        time_until_delivery = logic.hours_until(delivery.eta)
        shortfall_hours = time_until_delivery - remaining_hours

        backup = logic.find_backup_supplier(order.product, exclude_supplier_id=order.supplier_id)
        severity = "critical" if shortfall_hours > 3 else "high"

        reason = (
            f"{order.product.title()} delivery is delayed ({delivery.delay_info or 'no ETA update'}), "
            f"now arriving in {time_until_delivery:.1f}h. Current stock covers {remaining_hours:.1f}h "
            f"at {item.avg_usage_per_hour:g}/hr usage, leaving a {shortfall_hours:.1f}h gap."
        )
        if backup:
            reason += f" {backup.name} can supply {order.product} as a backup."
            message = f"Switch to backup supplier for {order.product}"
        else:
            reason += " No backup supplier is available for this product."
            message = f"Expedite {order.product} delivery or ration remaining stock"

        recommendation = Recommendation(
            id=store.new_id(),
            product=order.product,
            order_id=order.id,
            severity=severity,
            message=message,
            reason=reason,
            backup_supplier_id=backup.id if backup else None,
        )
        store.recommendations[recommendation.id] = recommendation
        new_recommendations.append(recommendation)

    products_with_delay_recommendation = {r.product for r in new_recommendations}
    for item in store.inventory.values():
        if item.product in products_with_delay_recommendation:
            continue
        if not logic.is_below_minimum(item):
            continue

        deficit = item.minimum_required_quantity - item.current_quantity
        reason = (
            f"{item.product.title()} stock ({item.current_quantity:g}) has fallen below the required "
            f"minimum ({item.minimum_required_quantity:g}), a deficit of {deficit:g} units."
        )
        recommendation = Recommendation(
            id=store.new_id(),
            product=item.product,
            order_id=None,
            severity="high",
            message=f"Replenish {item.product} stock",
            reason=reason,
        )
        store.recommendations[recommendation.id] = recommendation
        new_recommendations.append(recommendation)

    new_recommendations.sort(key=lambda r: SEVERITY_RANK.get(r.severity, 2))
    return new_recommendations


def accept_recommendation(recommendation_id: str) -> Recommendation:
    recommendation = store.recommendations.get(recommendation_id)
    if recommendation is None:
        raise KeyError(recommendation_id)

    recommendation.status = RecommendationStatus.ACCEPTED
    recommendation.accepted_at = datetime.utcnow()

    if recommendation.order_id and recommendation.backup_supplier_id:
        order = store.orders.get(recommendation.order_id)
        if order:
            order.supplier_id = recommendation.backup_supplier_id
            order.status = OrderStatus.ON_TIME
            delivery = store.deliveries.get(order.id)
            if delivery:
                delivery.status = OrderStatus.ON_TIME
                delivery.delay_info = f"Switched to backup supplier {recommendation.backup_supplier_id}"
    elif recommendation.order_id is None:
        item = store.inventory.get(recommendation.product)
        if item:
            item.current_quantity = item.minimum_required_quantity + item.avg_usage_per_hour * 4

    return recommendation
