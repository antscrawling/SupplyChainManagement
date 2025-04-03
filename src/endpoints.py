from fastapi import APIRouter, Depends, HTTPException, status, File, UploadFile
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
from .models import Customer, Order, OrderItem, Document
from .database import get_db
from pydantic import BaseModel

# Define the APIRouter
router = APIRouter(
    prefix="/orders",
    tags=["Orders"]
)

# Define Pydantic models for request/response
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

# Define endpoints
@router.post("/", response_model=OrderResponse)
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

@router.get("/{order_id}", response_model=OrderResponse)
async def get_order(order_id: int, db: Session = Depends(get_db)):
    # Logic for retrieving an order
    pass