import uvicorn
import os
import logging
from dotenv import load_dotenv
from pathlib import Path
from fastapi import FastAPI
from src.CustomerOnboarding import router

# Load environment variables
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(dotenv_path=env_path)

# Configure logging
logging.basicConfig(
    level=logging.DEBUG if os.getenv("ENV") == "development" else logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Create the FastAPI app object
app = FastAPI()

# Include the router
app.include_router(router, prefix="/customers")

# Ensure the app object is exposed at the module level
__all__ = ["app"]

def start_server():
    """Initialize and start the FastAPI server"""
    logger.debug("Starting FastAPI server in debug mode...")
    uvicorn.run(
        "src.main:app",  # Reference the app object in this module
        host="0.0.0.0",
        port=8080,  # Use port 8080
        reload=os.getenv("ENV") == "development",
        workers=int(os.getenv("WORKERS", 1))
    )

if __name__ == "__main__":
    start_server()