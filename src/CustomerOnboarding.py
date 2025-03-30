from datetime import datetime
from typing import Optional, List, Dict
from enum import Enum
from fastapi import FastAPI, HTTPException, status, File, UploadFile
from pydantic import BaseModel, EmailStr, Field, constr
import shutil
import os
from pathlib import Path

app = FastAPI(title="Supply Chain Customer Onboarding API")

class CustomerType(str, Enum):
    MANUFACTURER = "manufacturer"
    DISTRIBUTOR = "distributor"
    RETAILER = "retailer"
    SUPPLIER = "supplier"

class OnboardingStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    REJECTED = "rejected"

class CustomerProfile(BaseModel):
    company_name: constr(min_length=1, max_length=100)
    customer_type: CustomerType
    tax_id: constr(min_length=1, max_length=20)
    registration_date: datetime
    contact_email: EmailStr
    contact_phone: constr(pattern=r'^\+?1?\d{9,15}$')
    address: constr(min_length=1, max_length=200)
    credit_score: Optional[float] = Field(None, ge=0, le=1850)
    approved_credit_limit: Optional[float] = Field(None, ge=0)

    class Config:
        json_schema_extra = {
            "example": {
                "company_name": "ABC Manufacturing",
                "customer_type": "manufacturer",
                "tax_id": "123456789",
                "registration_date": "2025-03-29T12:00:00",
                "contact_email": "contact@abc.com",
                "contact_phone": "+1234567890",
                "address": "123 Business St",
                "credit_score": 750,
                "approved_credit_limit": 100000.0
            }
        }

class CustomerResponse(BaseModel):
    id: int
    company_name: str
    tax_id: str
    customer_type: CustomerType
    registration_date: datetime
    contact_email: EmailStr
    contact_phone: str
    address: str
    credit_score: Optional[float]
    approved_credit_limit: Optional[float]
    onboarding_status: OnboardingStatus
    created_at: datetime
    updated_at: datetime

class DocumentType(str, Enum):
    TAX_CERTIFICATE = "tax_certificate"
    BUSINESS_LICENSE = "business_license"
    CREDIT_REPORT = "credit_report"
    BANK_STATEMENT = "bank_statement"

class DocumentStatus(str, Enum):
    PENDING = "pending"
    VERIFIED = "verified"
    REJECTED = "rejected"

class Document(BaseModel):
    document_type: DocumentType
    file_name: str
    upload_date: datetime = Field(default_factory=datetime.utcnow)
    status: DocumentStatus = DocumentStatus.PENDING

class CustomerOnboarding:
    def __init__(self):
        self.customers: Dict[str, CustomerProfile] = {}
        self.onboarding_status: Dict[str, OnboardingStatus] = {}

# Create uploads directory if it doesn't exist
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

# Initialize the CustomerOnboarding instance
onboarding_service = CustomerOnboarding()

@app.post("/customers/", status_code=status.HTTP_201_CREATED)
async def create_customer(customer: CustomerProfile):
    if customer.company_name in onboarding_service.customers:
        raise HTTPException(
            status_code=400,
            detail="Customer with this company name already exists"
        )
    
    onboarding_service.customers[customer.company_name] = customer
    onboarding_service.onboarding_status[customer.company_name] = OnboardingStatus.PENDING
    return {"message": "Customer onboarding initiated", "customer": customer}

@app.post("/customers/batch", status_code=status.HTTP_201_CREATED)
async def create_customers_batch(customers: List[CustomerProfile]):
    created_customers = []
    for customer in customers:
        if customer.company_name in onboarding_service.customers:
            continue
        
        onboarding_service.customers[customer.company_name] = customer
        onboarding_service.onboarding_status[customer.company_name] = OnboardingStatus.PENDING
        created_customers.append(customer)
    
    return {
        "message": f"Created {len(created_customers)} customers",
        "customers": created_customers
    }

@app.get("/customers/{company_name}")
async def get_customer(company_name: str):
    #if company_name in 
    if company_name not in onboarding_service.customers:
        raise HTTPException(
            status_code=404,
            detail="Customer not found"
        )
    return onboarding_service.customers[company_name]

@app.get("/customers/")
async def list_customers():
    return list(onboarding_service.customers.values())

@app.put("/customers/{company_name}/status")
async def update_status(company_name: str, status: OnboardingStatus):
    if company_name not in onboarding_service.onboarding_status:
        raise HTTPException(
            status_code=404,
            detail="Customer not found"
        )
    onboarding_service.onboarding_status[company_name] = status
    return {"message": f"Status updated to {status}"}

@app.get("/customers/pending/")
async def get_pending_customers():
    return [
        company_name for company_name, status in onboarding_service.onboarding_status.items()
        if status == OnboardingStatus.PENDING
    ]

@app.post("/customers/{company_name}/documents/")
async def upload_document(
    company_name: str,
    document_type: DocumentType,
    file: UploadFile = File(...),
):
    if company_name not in onboarding_service.customers:
        raise HTTPException(
            status_code=404,
            detail="Customer not found"
        )
    
    # Create customer directory if it doesn't exist
    customer_dir = UPLOAD_DIR / company_name
    customer_dir.mkdir(exist_ok=True)
    
    # Save file
    file_path = customer_dir / f"{document_type}_{file.filename}"
    with file_path.open("wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    # Create document record
    document = Document(
        document_type=document_type,
        file_name=file_path.name,
    )
    
    # Add to customer's documents
    if not hasattr(onboarding_service.customers[company_name], 'documents'):
        onboarding_service.customers[company_name].documents = []
    onboarding_service.customers[company_name].documents.append(document)
    
    return {
        "message": "Document uploaded successfully",
        "document": document
    }

@app.get("/customers/{company_name}/documents/")
async def list_documents(company_name: str):
    if company_name not in onboarding_service.customers:
        raise HTTPException(
            status_code=404,
            detail="Customer not found"
        )
    
    customer = onboarding_service.customers[company_name]
    return getattr(customer, 'documents', [])

@app.put("/customers/{company_name}/documents/{document_type}/verify")
async def verify_document(
    company_name: str,
    document_type: DocumentType,
    status: DocumentStatus
):
    if company_name not in onboarding_service.customers:
        raise HTTPException(
            status_code=404,
            detail="Customer not found"
        )
    
    customer = onboarding_service.customers[company_name]
    documents = getattr(customer, 'documents', [])
    
    for doc in documents:
        if doc.document_type == document_type:
            doc.status = status
            return {"message": f"Document status updated to {status}"}
    
    raise HTTPException(
        status_code=404,
        detail=f"Document of type {document_type} not found"
    )