import logging
from fastapi import FastAPI

from app.api.nyt import router as nyt_router

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

app = FastAPI(
    title="NY Times Article Microservice",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.include_router(nyt_router)
