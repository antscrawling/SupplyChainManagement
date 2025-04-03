from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship, declarative_base
from datetime import datetime

Base = declarative_base()

# Customer Model
class Customer(Base):
    __tablename__ = "customers"

    id = Column(Integer, primary_key=True, index=True)
    company_name = Column(String, unique=True, index=True)
    customer_type = Column(String)
    tax_id = Column(String)
    registration_date = Column(DateTime, default=datetime.utcnow)
    contact_email = Column(String)
    contact_phone = Column(String)
    address = Column(String)
    credit_score = Column(Integer)
    approved_credit_limit = Column(Float)
    status = Column(String, default="pending")

# Order Model
class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False)
    order_date = Column(DateTime, default=datetime.utcnow)
    total_amount = Column(Float, nullable=False)
    status = Column(String, default="pending")

    items = relationship("OrderItem", back_populates="order")

# OrderItem Model
class OrderItem(Base):
    __tablename__ = "order_items"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False)
    product_name = Column(String, nullable=False)
    quantity = Column(Integer, nullable=False)
    unit_price = Column(Float, nullable=False)

    order = relationship("Order", back_populates="items")

# Document Model
class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False)
    document_type = Column(String, nullable=False)
    file_path = Column(String, nullable=False)
    upload_date = Column(DateTime, default=datetime.utcnow)
    status = Column(String, default="pending")