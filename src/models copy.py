from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, Enum, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from .CustomerOnboarding import CustomerType, OnboardingStatus

Base = declarative_base()

class Customer(Base):
    __tablename__ = "customers"

    id = Column(Integer, primary_key=True, index=True)
    company_name = Column(String(100), unique=True, index=True, nullable=False)
    customer_type = Column(Enum(CustomerType), nullable=False)
    tax_id = Column(String(20), unique=True, nullable=False)
    registration_date = Column(DateTime, default=datetime.utcnow)
    contact_email = Column(String(100), nullable=False)
    contact_phone = Column(String(20), nullable=False)
    address = Column(String(200), nullable=False)
    credit_score = Column(Float)
    approved_credit_limit = Column(Float)
    onboarding_status = Column(Enum(OnboardingStatus), default=OnboardingStatus.PENDING)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    orders = relationship("Order", back_populates="customer")
    documents = relationship("Document", back_populates="customer")

class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("customers.id"))
    order_date = Column(DateTime, default=datetime.utcnow)
    total_amount = Column(Float, nullable=False)
    status = Column(String(50), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    customer = relationship("Customer", back_populates="orders")
    items = relationship("OrderItem", back_populates="order")

class OrderItem(Base):
    __tablename__ = "order_items"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"))
    product_name = Column(String(100), nullable=False)
    quantity = Column(Integer, nullable=False)
    unit_price = Column(Float, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    order = relationship("Order", back_populates="items")

class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("customers.id"))
    document_type = Column(String(50), nullable=False)
    file_path = Column(String(255), nullable=False)
    upload_date = Column(DateTime, default=datetime.utcnow)
    status = Column(String(50), nullable=False)
    
    # Relationships
    customer = relationship("Customer", back_populates="documents")