import pytest
from fastapi.testclient import TestClient
from src.CustomerOnboarding import create_app

# Create the app instance for testing
app = create_app()
client = TestClient(app)

def test_create_customer():
    payload = {
        "company_name": "Test Company",
        "customer_type": "manufacturer",
        "tax_id": "TX123456999",
        "registration_date": "2025-03-31T12:00:00",
        "contact_email": "test@company.com",
        "contact_phone": "+1234567890",
        "address": "123 Test St",
        "credit_score": 800,
        "approved_credit_limit": 500000.0
    }
    response = client.post("/customers/", json=payload)
    assert response.status_code == 201
    assert "message" in response.json()
    assert response.json()["message"] == "Customer onboarding initiated"

def test_create_customers_batch():
    payload = [
        {
            "company_name": "Batch Company 1",
            "customer_type": "supplier",
            "tax_id": "TX123456888",
            "registration_date": "2025-03-31T12:00:00",
            "contact_email": "batch1@company.com",
            "contact_phone": "+1234567891",
            "address": "123 Batch St",
            "credit_score": 750,
            "approved_credit_limit": 300000.0
        },
        {
            "company_name": "Batch Company 2",
            "customer_type": "retailer",
            "tax_id": "TX123456777",
            "registration_date": "2025-03-31T12:00:00",
            "contact_email": "batch2@company.com",
            "contact_phone": "+1234567892",
            "address": "456 Batch St",
            "credit_score": 700,
            "approved_credit_limit": 200000.0
        }
    ]
    response = client.post("/customers/batch", json=payload)
    assert response.status_code == 201
    assert "message" in response.json()
    assert response.json()["message"] == "Created 2 customers"

def test_get_customer():
    company_name = "Test Company"
    response = client.get(f"/customers/{company_name}")
    assert response.status_code == 200
    assert "company_name" in response.json()
    assert response.json()["company_name"] == company_name

def test_list_customers():
    response = client.get("/customers/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_update_status():
    company_name = "Test Company"
    payload = {"status": "completed"}
    response = client.put(f"/customers/{company_name}/status", json=payload)
    assert response.status_code == 200
    assert "message" in response.json()
    assert response.json()["message"] == "Status updated to completed"

def test_get_pending_customers():
    response = client.get("/customers/pending/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)