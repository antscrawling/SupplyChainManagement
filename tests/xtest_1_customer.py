import pytest
from src.database import Base, engine

from fastapi.testclient import TestClient
from src.main import app
import uuid

client = TestClient(app)

@pytest.fixture(autouse=True)
def setup_and_teardown():
    # Drop and recreate tables for each test
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)
    
    
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
    
    