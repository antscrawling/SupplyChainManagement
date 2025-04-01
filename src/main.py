import uvicorn
import os
from dotenv import load_dotenv
from pathlib import Path
from .CustomerOnboarding import xcreate_app  # Import the FastAPI app creation function

# Load environment variables
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(dotenv_path=env_path)

# Create the app object at the module level
app = xcreate_app()  # Initialize the FastAPI app

# Ensure the app object is exposed at the module level
# This allows Uvicorn to find it when running "uvicorn src.main:app"
__all__ = ["app"]

def start_server():
    """Initialize and start the FastAPI server"""
    uvicorn.run(
        "src.main:app",  # Reference the app object in this module
        host="0.0.0.0",
        port=8080,  # Use port 8080
        reload=os.getenv("ENV") == "development",
        workers=int(os.getenv("WORKERS", 1))
    )

if __name__ == "__main__":
    start_server()