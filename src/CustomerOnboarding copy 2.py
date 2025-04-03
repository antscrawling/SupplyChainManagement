from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List
from datetime import datetime
from sqlalchemy import Column, String, Integer, Float, DateTime
from sqlalchemy.orm import declarative_base, Session
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

router = APIRouter()

# SQLAlchemy setup
Base = declarative_base()
engine = create_engine("sqlite:///./test.db", connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

class CustomerModel(Base):
    __tablename__ = "customers"

    company_name = Column(String, primary_key=True, index=True)
    customer_type = Column(String)
    tax_id = Column(String)
    registration_date = Column(DateTime)
    contact_email = Column(String)
    contact_phone = Column(String)
    address = Column(String)
    credit_score = Column(Integer)
    approved_credit_limit = Column(Float)
    status = Column(String, default="pending")

Base.metadata.create_all(bind=engine)

class Customer(BaseModel):
    company_name: str
    customer_type: str
    tax_id: str
    registration_date: datetime
    contact_email: str
    contact_phone: str
    address: str
    credit_score: int
    approved_credit_limit: float
    status: str = "pending"

    class Config:
        orm_mode = True

class StatusUpdate(BaseModel):
    status: str

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/", status_code=201)
def create_customer(customer: Customer, db: Session = Depends(get_db)):
    db_customer = CustomerModel(**customer.dict())
    db.add(db_customer)
    db.commit()
    return {"message": "Customer created successfully"}

@router.post("/batch", status_code=201)
def create_customers_batch(customers: List[Customer], db: Session = Depends(get_db)):
    existing_names = {cust.company_name for cust in db.query(CustomerModel).all()}
    duplicates = [cust.company_name for cust in customers if cust.company_name in existing_names]
    if duplicates:
        raise HTTPException(
            status_code=400,
            detail=f"Duplicate company names found: {', '.join(duplicates)}"
        )
    db_customers = [CustomerModel(**cust.dict()) for cust in customers]
    db.add_all(db_customers)
    db.commit()
    return {"message": f"{len(customers)} customers created successfully"}

@router.get("/{company_name}")
def get_customer(company_name: str, db: Session = Depends(get_db)):
    customer = db.query(CustomerModel).filter(CustomerModel.company_name == company_name).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    return customer

@router.get("/")
def list_customers(db: Session = Depends(get_db)):
    return db.query(CustomerModel).all()

@router.put("/{company_name}/status")
def update_customer_status(company_name: str, update: StatusUpdate, db: Session = Depends(get_db)):
    customer = db.query(CustomerModel).filter(CustomerModel.company_name == company_name).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    customer.status = update.status
    db.commit()
    return {"message": "Status updated successfully"}

@router.get("/pending/")
def get_pending_customers(db: Session = Depends(get_db)):
    return db.query(CustomerModel).filter(CustomerModel.status == "pending").all()
