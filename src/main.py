import uvicorn
import os
import logging
from dotenv import load_dotenv
from pathlib import Path
from fastapi import FastAPI
#from src.CustomerOnboarding import router  # Import the router from CustomerOnboarding
from src.CustomerOnboarding import router  # Import the router from masterendpoint
from CustomerOnboarding import router  # Import the router from CustomerOnboarding

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
app.include_router(router)


if __name__ == "__main__":
    uvicorn.run("app", host="0.0.0.0", port=8080, reload=True)