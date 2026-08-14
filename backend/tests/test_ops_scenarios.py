from fastapi.testclient import TestClient

from app.main import create_app


def client() -> TestClient:
    return TestClient(create_app())


def test_normal_day_produces_no_recommendations():
    c = client()
    response = c.post("/ops/scenarios/normal/trigger")
    assert response.status_code == 200
    assert response.json() == []


def test_supplier_delay_flags_shortage_and_recommends_backup():
    c = client()
    response = c.post("/ops/scenarios/supplier_delay/trigger")
    recommendations = response.json()
    assert len(recommendations) == 1
    assert recommendations[0]["product"] == "milk"
    assert recommendations[0]["backup_supplier_id"] == "supplier-milk-backup"

    dashboard = c.get("/ops/dashboard").json()
    milk_order = next(o for o in dashboard["orders"] if o["product"] == "milk")
    assert milk_order["status"] == "at_risk"


def test_multiple_delays_ranks_more_urgent_product_first():
    c = client()
    response = c.post("/ops/scenarios/multiple_delays/trigger")
    recommendations = response.json()
    assert [r["product"] for r in recommendations] == ["flour", "milk"]
    assert recommendations[0]["severity"] == "critical"


def test_inventory_shortage_recommends_replenishment_without_delay():
    c = client()
    response = c.post("/ops/scenarios/inventory_shortage/trigger")
    recommendations = response.json()
    assert len(recommendations) == 1
    assert recommendations[0]["product"] == "flour"
    assert recommendations[0]["order_id"] is None
    assert "Replenish" in recommendations[0]["message"]


def test_accepting_a_backup_supplier_recommendation_updates_the_order():
    c = client()
    recommendations = c.post("/ops/scenarios/supplier_delay/trigger").json()
    recommendation_id = recommendations[0]["id"]

    accept_response = c.post(f"/ops/recommendations/{recommendation_id}/accept")
    assert accept_response.status_code == 200
    assert accept_response.json()["status"] == "accepted"

    dashboard = c.get("/ops/dashboard").json()
    milk_order = next(o for o in dashboard["orders"] if o["product"] == "milk")
    assert milk_order["status"] == "on_time"
    assert milk_order["supplier_name"] == "Valley Dairy Co-op"
    assert dashboard["delivery_summary"].get("at_risk", 0) == 0
