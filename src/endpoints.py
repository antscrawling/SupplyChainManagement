from fastapi import APIRouter, Depends, HTTPException, status, File, UploadFile
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
from .models import Customer, Order, OrderItem, Document
from .models import CustomerType, OnboardingStatus
from .database import get_db
from pydantic import BaseModel, Field

router = APIRouter()

# Pydantic models for request/response
class OrderItemCreate(BaseModel):
    product_name: str
    quantity: int
    unit_price: float

class OrderCreate(BaseModel):
    customer_id: int
    items: List[OrderItemCreate]

class OrderResponse(BaseModel):
    id: int
    customer_id: int
    order_date: datetime
    total_amount: float
    status: str
    items: List[OrderItemCreate]

class DocumentResponse(BaseModel):
    id: int
    customer_id: int
    document_type: str
    file_path: str
    upload_date: datetime
    status: str

# Order endpoints
@router.post("/orders/", response_model=OrderResponse)
async def create_order(order: OrderCreate, db: Session = Depends(get_db)):
    # Calculate total amount
    total_amount = sum(item.quantity * item.unit_price for item in order.items)
    
    db_order = models.Order(
        customer_id=order.customer_id,
        total_amount=total_amount,
        status="pending"
    )
    db.add(db_order)
    db.flush()  # Get the order ID
    
    # Create order items
    for item in order.items:
        db_item = models.OrderItem(
            order_id=db_order.id,
            product_name=item.product_name,
            quantity=item.quantity,
            unit_price=item.unit_price
        )
        db.add(db_item)
    
    db.commit()
    db.refresh(db_order)
    return db_order

@router.get("/orders/{order_id}", response_model=OrderResponse)
async def get_order(order_id: int, db: Session = Depends(get_db)):
    order = db.query(models.Order).filter(models.Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order

@router.get("/customers/{customer_id}/orders/", response_model=List[OrderResponse])
async def list_customer_orders(customer_id: int, db: Session = Depends(get_db)):
    orders = db.query(models.Order).filter(models.Order.customer_id == customer_id).all()
    return orders

# Document endpoints
@router.post("/customers/{customer_id}/documents/")
async def upload_document(
    customer_id: int,
    document_type: str,
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    # Verify customer exists
    customer = db.query(models.Customer).filter(models.Customer.id == customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    
    # Save file and create document record
    file_path = f"uploads/{customer_id}/{document_type}_{file.filename}"
    
    db_document = models.Document(
        customer_id=customer_id,
        document_type=document_type,
        file_path=file_path,
        status="pending"
    )
    db.add(db_document)
    db.commit()
    db.refresh(db_document)
    
    return {"message": "Document uploaded successfully", "document_id": db_document.id}

@router.get("/customers/{customer_id}/documents/", response_model=List[DocumentResponse])
async def list_customer_documents(customer_id: int, db: Session = Depends(get_db)):
    documents = db.query(models.Document).filter(
        models.Document.customer_id == customer_id
    ).all()
    return documents

# OrderItem endpoints
@router.put("/orders/{order_id}/items/{item_id}")
async def update_order_item(
    order_id: int,
    item_id: int,
    item: OrderItemCreate,
    db: Session = Depends(get_db)
):
    db_item = db.query(models.OrderItem).filter(
        models.OrderItem.id == item_id,
        models.OrderItem.order_id == order_id
    ).first()
    
    if not db_item:
        raise HTTPException(status_code=404, detail="Order item not found")
    
    db_item.product_name = item.product_name
    db_item.quantity = item.quantity
    db_item.unit_price = item.unit_price
    
    # Update order total
    order = db.query(models.Order).filter(models.Order.id == order_id).first()
    order.total_amount = sum(
        item.quantity * item.unit_price 
        for item in order.items
    )
    
    db.commit()
    db.refresh(db_item)
    return db_item