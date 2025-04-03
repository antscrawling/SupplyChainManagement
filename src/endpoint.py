from fastapi import APIRouter
from src.CustomerOnboarding import router as customer_router
from src.endpoints import router as order_router

# Create a central APIRouter
api_router = APIRouter()

# Include routers from different modules
api_router.include_router(customer_router, prefix="/customers", tags=["Customers"])
api_router.include_router(order_router, prefix="/orders", tags=["Orders"])