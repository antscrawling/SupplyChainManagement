import pytest
from fastapi.testclient import TestClient
from src.main import app
import uuid
from itertools import count
from random import randrange as randbetween

client = TestClient(app)

@pytest.fixture(autouse=True)
def clear_database():
    # Drop all tables and recreate them before each test
    from src.CustomerOnboarding import Base, engine
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield

def generate_unique_name(base_name: str) -> str:
    """Generate a unique name by appending a UUID suffix."""
    return f"{base_name}_{uuid.uuid4().hex[:8]}"

def test_create_customer():
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
    response = client.post("/api/customers/", json=payload)  # Corrected endpoint
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
    response = client.post("/api/customers/batch", json=payload)  # Corrected endpoint
    assert response.status_code == 201

def test_get_customer():
    unique_name = generate_unique_name("Test Company")
    payload = {
        "company_name": unique_name,
        "customer_type": "manufacturer",
        "tax_id": "TX123456999",
        "registration_date": "2025-03-31T12:00:00",
        "contact_email": "test@company.com",
        "contact_phone": "+1234567890",
        "address": "123 Test St",
        "credit_score": 800,
        "approved_credit_limit": 500000.0,
        "status": "pending"
    }
    client.post("/api/customers/", json=payload)  # Corrected endpoint
    response = client.get(f"/api/customers/{unique_name}")  # Corrected endpoint
    assert response.status_code == 200

def test_get_non_existent_customer():
    unique_name = generate_unique_name("NonExistent Company")
    response = client.get(f"/api/customers/{unique_name}")  # Corrected endpoint
    assert response.status_code == 404
    assert response.json()["detail"] == "Customer not found"

def test_list_customers_empty():
    response = client.get("/api/customers/")  # Corrected endpoint
    assert response.status_code == 200
    assert response.json() == []
