import pytest
from fastapi.testclient import TestClient
from src.main import app
from src.CustomerOnboarding import Base, engine, SessionLocal
import uuid
from itertools import count
from random import randrange as randbetween

client = TestClient(app)

@pytest.fixture(autouse=True)
def clear_database():
    # Drop all tables and recreate them before each test
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield

@pytest.fixture
def generate_unique_name():
    """Generate a unique name by appending a UUID suffix."""
    return lambda base_name: f"{base_name}_{uuid.uuid4().hex[:8]}"

@pytest.fixture
def db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@pytest.fixture
def create_customer(generate_unique_name):
    """Create a consistent customer for use in tests."""
    unique_name = generate_unique_name("Test Company")
    customer_payload = {
        "company_name": unique_name,
        "customer_type": "manufacturer",
        "tax_id": f"TX12345699{randbetween(1,100)}",
        "registration_date": "2025-03-31T12:00:00",
        "contact_email": "test@company.com",
        "contact_phone": "+1234567890",
        "address": "123 Test St",
        "credit_score": 800,
        "approved_credit_limit": 500000.0,
        "status": "pending"
    }
    response = client.post("/api/customers/", json=customer_payload)
    assert response.status_code == 201
    return unique_name

# Customer Tests
def test_create_customer(generate_unique_name):
    unique_name = generate_unique_name("Test Company")
    payload = {
        "company_name": unique_name,
        "customer_type": "manufacturer",
        "tax_id": f"TX12345699{randbetween(1,100)}",
        "registration_date": "2025-03-31T12:00:00",
        "contact_email": "test@company.com",
        "contact_phone": "+1234567890",
        "address": "123 Test St",
        "credit_score": 800,
        "approved_credit_limit": 500000.0,
        "status": "pending"
    }
    response = client.post("/api/customers/", json=payload)
    assert response.status_code == 201

def test_create_customers_batch():
    mycounter = count(7)
    xcounter = randbetween(1, 9)
    unique_name_1 = f'Batch Company {xcounter}{next(mycounter)}'
    unique_name_2 = f'Batch Company {xcounter}{next(mycounter)}'
    payload = [
        {
            "company_name": unique_name_1,
            "customer_type": "supplier",
            "tax_id": "TX123456888",
            "registration_date": "2025-03-31T12:00:00",
            "contact_email": "batch1@company.com",
            "contact_phone": "+1234567891",
            "address": "123 Batch St",
            "credit_score": 750,
            "approved_credit_limit": 300000.0,
            "status": "pending"
        },
        {
            "company_name": unique_name_2,
            "customer_type": "retailer",
            "tax_id": "TX123456777",
            "registration_date": "2025-03-31T12:00:00",
            "contact_email": "batch2@company.com",
            "contact_phone": "+1234567892",
            "address": "456 Batch St",
            "credit_score": 700,
            "approved_credit_limit": 200000.0,
            "status": "pending"
        }
    ]
    response = client.post("/api/customers/batch", json=payload)
    assert response.status_code == 201

def test_get_customer(create_customer):
    customer_name = create_customer
    response = client.get(f"/api/customers/{customer_name}")
    assert response.status_code == 200

def test_list_customers_empty():
    response = client.get("/api/customers/")
    assert response.status_code == 200
    assert response.json() == []

# Order Tests
def test_create_order(create_customer):
    # Use the consistent customer created by the fixture
    customer_name = create_customer

    # Create an order for the customer
    order_payload = {
        "customer_id": customer_name,
        "items": [
            {"product_name": "Laptop", "quantity": 2, "unit_price": 1200.50},
            {"product_name": "Mouse", "quantity": 5, "unit_price": 25.00}
        ]
    }
    response = client.post("/api/orders/", json=order_payload)
    assert response.status_code == 201
    assert response.json()["total_amount"] == 2450.50

def test_get_order(create_customer):
    # Use the consistent customer created by the fixture
    customer_name = create_customer

    # Create an order for the customer
    order_payload = {
        "customer_id": customer_name,
        "items": [
            {"product_name": "Laptop", "quantity": 2, "unit_price": 1200.50},
            {"product_name": "Mouse", "quantity": 5, "unit_price": 25.00}
        ]
    }
    client.post("/api/orders/", json=order_payload)

    # Retrieve the order
    response = client.get("/api/orders/1")
    assert response.status_code == 200
    assert response.json()["id"] == 1

def test_list_orders(create_customer):
    # Use the consistent customer created by the fixture
    customer_name = create_customer

    # Create an order for the customer
    order_payload = {
        "customer_id": customer_name,
        "items": [
            {"product_name": "Laptop", "quantity": 2, "unit_price": 1200.50},
            {"product_name": "Mouse", "quantity": 5, "unit_price": 25.00}
        ]
    }
    client.post("/api/orders/", json=order_payload)

    # List all orders
    response = client.get("/api/orders/")
    assert response.status_code == 200
    assert len(response.json()) > 0