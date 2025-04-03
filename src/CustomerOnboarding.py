from fastapi import APIRouter, HTTPException, Depends, status, File, UploadFile
from pydantic import BaseModel
from typing import List
from datetime import datetime
from sqlalchemy import Column, String, Integer, Float, DateTime, ForeignKey
from sqlalchemy.orm import declarative_base, Session, relationship
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os

print("Current working directory:", os.getcwd())

# Use an absolute path for the database
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE_URL = f"sqlite:///{os.path.join(BASE_DIR, 'test.db')}"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

# Define the APIRouter
router = APIRouter(
    prefix="/api",
    tags=["API"]
)

# SQLAlchemy setup
Base = declarative_base()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Define the CustomerModel
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

# Define the Order model
class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(String, ForeignKey("customers.company_name"))
    order_date = Column(DateTime, default=datetime.utcnow)
    total_amount = Column(Float)
    status = Column(String, default="pending")
    items = relationship("OrderItem", back_populates="order")

# Define the OrderItem model
class OrderItem(Base):
    __tablename__ = "order_items"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"))
    product_name = Column(String)
    quantity = Column(Integer)
    unit_price = Column(Float)
    order = relationship("Order", back_populates="items")

# Create the database tables
Base.metadata.create_all(bind=engine)
print("Database tables created successfully.")

# Define the Pydantic models
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

class OrderItemCreate(BaseModel):
    product_name: str
    quantity: int
    unit_price: float

class OrderCreate(BaseModel):
    customer_id: str
    items: List[OrderItemCreate]

class OrderResponse(BaseModel):
    id: int
    customer_id: str
    order_date: datetime
    total_amount: float
    status: str
    items: List[OrderItemCreate]

    class Config:
        orm_mode = True

# Dependency to get the database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Define the customer endpoints
@router.post("/customers/", status_code=201)
def create_customer(customer: Customer, db: Session = Depends(get_db)):
    db_customer = CustomerModel(**customer.dict())
    db.add(db_customer)
    db.commit()
    return {"message": "Customer created successfully"}

@router.post("/customers/batch", status_code=201)
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

@router.get("/customers/{company_name}")
def get_customer(company_name: str, db: Session = Depends(get_db)):
    customer = db.query(CustomerModel).filter(CustomerModel.company_name == company_name).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    return customer

@router.get("/customers/")
def list_customers(db: Session = Depends(get_db)):
    return db.query(CustomerModel).all()

@router.put("/customers/{company_name}/status")
def update_customer_status(company_name: str, update: StatusUpdate, db: Session = Depends(get_db)):
    customer = db.query(CustomerModel).filter(CustomerModel.company_name == company_name).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    customer.status = update.status
    db.commit()
    return {"message": "Status updated successfully"}

@router.get("/customers/pending/")
def get_pending_customers(db: Session = Depends(get_db)):
    return db.query(CustomerModel).filter(CustomerModel.status == "pending").all()

# Define the order endpoints
@router.post("/orders/", response_model=OrderResponse)
async def create_order(order: OrderCreate, db: Session = Depends(get_db)):
    # Calculate total amount
    total_amount = sum(item.quantity * item.unit_price for item in order.items)
    
    # Create the Order object
    db_order = Order(
        customer_id=order.customer_id,
        total_amount=total_amount,
        status="pending"
    )
    db.add(db_order)
    db.flush()  # Flush to get the order ID
    
    # Create OrderItem objects
    db_items = []
    for item in order.items:
        db_item = OrderItem(
            order_id=db_order.id,
            product_name=item.product_name,
            quantity=item.quantity,
            unit_price=item.unit_price
        )
        db.add(db_item)
        db_items.append(db_item)
    
    db.commit()
    db.refresh(db_order)

    # Return the response
    return {
        "id": db_order.id,
        "customer_id": db_order.customer_id,
        "order_date": db_order.order_date,
        "total_amount": db_order.total_amount,
        "status": db_order.status,
        "items": [
            {
                "product_name": item.product_name,
                "quantity": item.quantity,
                "unit_price": item.unit_price
            }
            for item in db_items
        ]
    }

@router.get("/orders/{order_id}", response_model=OrderResponse)
async def get_order(order_id: int, db: Session = Depends(get_db)):
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order