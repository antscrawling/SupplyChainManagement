import pytest
from fastapi.testclient import TestClient
from src.main import app
import uuid

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
        "tax_id": "TX123456999",
        "registration_date": "2025-03-31T12:00:00",
        "contact_email": "test@company.com",
        "contact_phone": "+1234567890",
        "address": "123 Test St",
        "credit_score": 800,
        "approved_credit_limit": 500000.0,
        "status": "pending"
    }
    response = client.post("/customers/", json=payload)
    assert response.status_code == 201

def test_create_customers_batch():
    unique_name_1 = generate_unique_name("Batch Company 1")
    unique_name_2 = generate_unique_name("Batch Company 2")
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
    response = client.post("/customers/batch", json=payload)
    assert response.status_code == 201

def test_create_customers_batch_with_duplicates():
    unique_name = generate_unique_name("Duplicate Company")
    payload = [
        {
            "company_name": unique_name,
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
            "company_name": unique_name,
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
    response = client.post("/customers/batch", json=payload)
    assert response.status_code == 400
    assert "Duplicate company names found" in response.json()["detail"]

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
    client.post("/customers/", json=payload)
    response = client.get(f"/customers/{unique_name}")
    assert response.status_code == 200

def test_get_non_existent_customer():
    unique_name = generate_unique_name("NonExistent Company")
    response = client.get(f"/customers/{unique_name}")
    assert response.status_code == 404
    assert response.json()["detail"] == "Customer not found"

def test_list_customers():
    unique_name_1 = generate_unique_name("Batch Company 1")
    unique_name_2 = generate_unique_name("Batch Company 2")
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
    client.post("/customers/batch", json=payload)
    response = client.get("/customers/")
    assert response.status_code == 200
    assert len(response.json()) == 2

def test_list_customers_empty():
    response = client.get("/customers/")
    assert response.status_code == 200
    assert response.json() == []

def test_update_status():
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
    client.post("/customers/", json=payload)
    update_payload = {"status": "completed"}
    response = client.put(f"/customers/{unique_name}/status", json=update_payload)
    assert response.status_code == 200

def test_update_status_non_existent_customer():
    unique_name = generate_unique_name("NonExistent Company")
    update_payload = {"status": "completed"}
    response = client.put(f"/customers/{unique_name}/status", json=update_payload)
    assert response.status_code == 404
    assert response.json()["detail"] == "Customer not found"

def test_update_status_invalid_value():
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
    client.post("/customers/", json=payload)

    # Attempt to update the status with an invalid value
    update_payload = {"status": "invalid_status"}
    response = client.put(f"/customers/{unique_name}/status", json=update_payload)
    assert response.status_code == 422

def test_get_pending_customers():
    unique_name_1 = generate_unique_name("Batch Company 1")
    unique_name_2 = generate_unique_name("Batch Company 2")
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
    client.post("/customers/batch", json=payload)
    response = client.get("/customers/pending/")
    assert response.status_code == 200
    assert len(response.json()) == 2

def test_create_duplicate_customer():
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
    # Create the first customer
    response = client.post("/customers/", json=payload)
    assert response.status_code == 201

    # Attempt to create the same customer again
    response = client.post("/customers/", json=payload)
    assert response.status_code == 400
    assert response.json()["detail"] == "Customer with this company name already exists"
