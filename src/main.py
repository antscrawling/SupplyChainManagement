import uvicorn
import os
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(dotenv_path=env_path)

def start_server():
    """Initialize and start the FastAPI server"""
    uvicorn.run(
        "CustomerOnboarding:app",
        host="0.0.0.0",
        port=int(os.getenv("API_PORT", 8000)),
        reload=os.getenv("ENV") == "development",
        workers=int(os.getenv("WORKERS", 1))
    )

if __name__ == "__main__":
    start_server()