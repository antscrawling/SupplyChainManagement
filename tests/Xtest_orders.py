import pytest
from fastapi.testclient import TestClient
from src.main import app
from src.CustomerOnboarding import Base, engine, SessionLocal
from sqlalchemy.orm import Session

client = TestClient(app)

# Test database setup/teardown
@pytest.fixture(autouse=True)
def setup_and_teardown():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def db() -> Session:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def test_create_order():
    # Create a customer first
    customer_payload = {
        "company_name": "Order Co",
        "customer_type": "manufacturer",
        "tax_id": "TX123456789",
        "registration_date": "2025-04-01T12:00:00",
        "contact_email": "orderco@example.com",
        "contact_phone": "+1234567890",
        "address": "123 Order St",
        "credit_score": 800,
        "approved_credit_limit": 500000.0,
        "status": "pending"
    }
    client.post("/customers/", json=customer_payload)

    # Create an order for the customer
    order_payload = {
        "customer_id": 1,
        "items": [
            {"product_name": "Laptop", "quantity": 2, "unit_price": 1200.50},
            {"product_name": "Mouse", "quantity": 5, "unit_price": 25.00}
        ]
    }
    response = client.post("/orders/", json=order_payload)
    assert response.status_code == 201
    assert response.json()["total_amount"] == 2450.50

def test_get_order():
    # Create an order first
    test_create_order()

    # Retrieve the order
    response = client.get("/orders/1")
    assert response.status_code == 200
    assert response.json()["id"] == 1

def test_list_orders():
    # Create multiple orders
    test_create_order()

    response = client.get("/orders/")
    assert response.status_code == 200
    assert len(response.json()) > 0
