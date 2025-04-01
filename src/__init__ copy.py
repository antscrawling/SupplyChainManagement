"""Supply Chain Management System

This package provides functionality for customer onboarding, order management,
and supply chain operations.
"""

from dotenv import load_dotenv
import os
from pathlib import Path

# Load environment variables from .env file
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(dotenv_path=env_path)

from .database import Base, engine, SessionLocal, get_db
from .models import Customer, Order, OrderItem, Document
from .CustomerOnboarding import CustomerType, OnboardingStatus, CustomerProfile

__version__ = "0.1.0"

__all__ = [
    # Database
    'Base',
    'engine',
    'SessionLocal',
    'get_db',
    
    # Models
    'Customer',
    'Order',
    'OrderItem',
    'Document',
    
    # Customer Onboarding
    'CustomerType',
    'OnboardingStatus',
    'CustomerProfile',
]