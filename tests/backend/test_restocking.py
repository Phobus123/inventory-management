"""
Tests for restocking API endpoints.
"""
import pytest


class TestRestockingRecommendationsEndpoint:
    """Test suite for GET /api/restocking/recommendations."""

    def test_get_recommendations_structure(self, client):
        """Test the recommendations response has the expected shape."""
        response = client.get("/api/restocking/recommendations?budget=10000")
        assert response.status_code == 200

        data = response.json()
        assert "budget" in data
        assert "recommended_items" in data
        assert "total_estimated_cost" in data
        assert "remaining_budget" in data
        assert "items_considered" in data
        assert "items_recommended" in data
        assert isinstance(data["recommended_items"], list)
        assert data["items_recommended"] == len(data["recommended_items"])

        if data["recommended_items"]:
            item = data["recommended_items"][0]
            for field in ["sku", "name", "warehouse", "category", "unit_cost",
                          "quantity_on_hand", "reorder_point", "current_demand",
                          "forecasted_demand", "trend", "gap", "recommended_quantity",
                          "estimated_cost"]:
                assert field in item

    def test_recommendations_sorted_by_urgency(self, client):
        """Test that recommended items are sorted by descending gap (most urgent first)."""
        response = client.get("/api/restocking/recommendations?budget=100000")
        assert response.status_code == 200

        items = response.json()["recommended_items"]
        gaps = [item["gap"] for item in items]
        assert gaps == sorted(gaps, reverse=True)

    def test_recommendations_stay_within_budget(self, client):
        """Test that the total estimated cost never exceeds the given budget."""
        response = client.get("/api/restocking/recommendations?budget=5000")
        assert response.status_code == 200

        data = response.json()
        assert data["total_estimated_cost"] <= 5000
        assert data["remaining_budget"] >= 0
        calculated_cost = sum(item["estimated_cost"] for item in data["recommended_items"])
        assert abs(data["total_estimated_cost"] - calculated_cost) < 0.01

    def test_zero_budget_returns_no_recommendations(self, client):
        """Test that a budget of 0 recommends nothing."""
        response = client.get("/api/restocking/recommendations?budget=0")
        assert response.status_code == 200

        data = response.json()
        assert data["recommended_items"] == []
        assert data["items_recommended"] == 0
        assert data["total_estimated_cost"] == 0

    def test_large_budget_recommends_all_eligible_items(self, client):
        """Test that a very large budget recommends every item with a positive demand gap."""
        response = client.get("/api/restocking/recommendations?budget=1000000")
        assert response.status_code == 200

        data = response.json()
        assert data["items_recommended"] == data["items_considered"]
        assert data["items_recommended"] > 0

    def test_negative_budget_returns_400(self, client):
        """Test that a negative budget is rejected."""
        response = client.get("/api/restocking/recommendations?budget=-100")
        assert response.status_code == 400

        data = response.json()
        assert "detail" in data

    def test_recommendations_filtered_by_warehouse(self, client):
        """Test filtering recommendations by warehouse."""
        response = client.get("/api/restocking/recommendations?budget=1000000&warehouse=Tokyo")
        assert response.status_code == 200

        data = response.json()
        for item in data["recommended_items"]:
            assert item["warehouse"] == "Tokyo"

    def test_recommendations_filtered_by_category(self, client):
        """Test filtering recommendations by category."""
        response = client.get("/api/restocking/recommendations?budget=1000000&category=Sensors")
        assert response.status_code == 200

        data = response.json()
        for item in data["recommended_items"]:
            assert item["category"].lower() == "sensors"

    def test_missing_budget_returns_422(self, client):
        """Test that budget is a required query parameter."""
        response = client.get("/api/restocking/recommendations")
        assert response.status_code == 422


class TestRestockingOrdersEndpoint:
    """Test suite for POST /api/restocking/orders."""

    def test_submit_order_with_sufficient_budget(self, client):
        """Test placing a restocking order returns a valid Order-shaped payload."""
        response = client.post("/api/restocking/orders", json={"budget": 20000})
        assert response.status_code == 201

        order = response.json()
        assert order["source"] == "restocking"
        assert order["status"] == "Submitted"
        assert order["order_number"].startswith("RST-2025-")
        assert order["customer"] == "Internal Restocking"
        assert isinstance(order["items"], list)
        assert len(order["items"]) > 0
        assert order["lead_time_days"] is not None
        assert 5 <= order["lead_time_days"] <= 10
        assert order["total_value"] > 0

    def test_submit_order_expected_delivery_matches_lead_time(self, client):
        """Test that expected_delivery is order_date + lead_time_days."""
        response = client.post("/api/restocking/orders", json={"budget": 20000})
        assert response.status_code == 201

        order = response.json()
        from datetime import datetime
        order_date = datetime.fromisoformat(order["order_date"])
        expected_delivery = datetime.fromisoformat(order["expected_delivery"])
        delta_days = (expected_delivery - order_date).days
        assert delta_days == order["lead_time_days"]

    def test_submit_order_with_zero_budget_returns_400(self, client):
        """Test that a budget too small to afford anything is rejected."""
        response = client.post("/api/restocking/orders", json={"budget": 0})
        assert response.status_code == 400

        data = response.json()
        assert "detail" in data

    def test_submit_order_with_negative_budget_returns_400(self, client):
        """Test that a negative budget is rejected."""
        response = client.post("/api/restocking/orders", json={"budget": -50})
        assert response.status_code == 400

    def test_submitted_order_appears_in_orders_list(self, client):
        """Test that a submitted restocking order is retrievable via GET /api/orders."""
        submit_response = client.post("/api/restocking/orders", json={"budget": 20000})
        assert submit_response.status_code == 201
        new_order = submit_response.json()

        orders_response = client.get("/api/orders")
        assert orders_response.status_code == 200
        all_orders = orders_response.json()

        matching = [o for o in all_orders if o["id"] == new_order["id"]]
        assert len(matching) == 1
        assert matching[0]["order_number"] == new_order["order_number"]
        assert matching[0]["source"] == "restocking"

    def test_submitted_order_retrievable_by_id(self, client):
        """Test that a submitted restocking order is retrievable via GET /api/orders/{id}."""
        submit_response = client.post("/api/restocking/orders", json={"budget": 20000})
        assert submit_response.status_code == 201
        new_order = submit_response.json()

        get_response = client.get(f"/api/orders/{new_order['id']}")
        assert get_response.status_code == 200
        assert get_response.json()["order_number"] == new_order["order_number"]

    def test_order_numbers_increment_across_submissions(self, client):
        """Test that consecutive restocking orders get distinct, incrementing order numbers."""
        first = client.post("/api/restocking/orders", json={"budget": 5000}).json()
        second = client.post("/api/restocking/orders", json={"budget": 5000}).json()

        assert first["order_number"] != second["order_number"]
        assert first["id"] != second["id"]

    def test_existing_orders_unaffected_by_restocking_submission(self, client):
        """Test that seed orders retain their shape and are not mutated by restocking submissions."""
        before = client.get("/api/orders").json()
        seed_orders_before = [o for o in before if o.get("source") != "restocking"]

        client.post("/api/restocking/orders", json={"budget": 5000})

        after = client.get("/api/orders").json()
        seed_orders_after = [o for o in after if o.get("source") != "restocking"]

        assert len(seed_orders_before) == len(seed_orders_after)

    def test_orders_category_filter_survives_categoryless_restocking_order(self, client):
        """A restocking order submitted without a category sets category=None on the order dict.
        GET /api/orders?category=... must not 500 once such an order exists in the merged list."""
        submit_response = client.post(
            "/api/restocking/orders", json={"budget": 20000, "category": "all"}
        )
        assert submit_response.status_code == 201
        assert submit_response.json()["category"] is None

        response = client.get("/api/orders?category=Sensors")
        assert response.status_code == 200
        for order in response.json():
            assert order["category"].lower() == "sensors"

    def test_orders_status_filter_survives_restocking_order(self, client):
        """GET /api/orders?status=... must not 500 once a 'Submitted' restocking order exists."""
        client.post("/api/restocking/orders", json={"budget": 20000})

        response = client.get("/api/orders?status=Delivered")
        assert response.status_code == 200
        for order in response.json():
            assert order["status"].lower() == "delivered"
