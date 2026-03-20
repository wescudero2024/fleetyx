import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

from app.infrastructure.database.database import init_db
from app.interfaces.api.routes import loads, quotes, tracking, carriers, matching, rates


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        await init_db()
    except Exception as e:
        # Log database initialization error but don't fail startup
        import logging
        logger = logging.getLogger(__name__)
        logger.warning(f"Database initialization failed: {e}")
    yield


app = FastAPI(
    title="Transportation Management System API",
    description="A scalable, production-ready TMS backend with clean architecture",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(loads.router)
app.include_router(quotes.router)
app.include_router(tracking.router)
app.include_router(carriers.router)
app.include_router(matching.router)
app.include_router(rates.router)


@app.get("/")
async def root():
    return {
        "success": True,
        "data": {
            "message": "Transportation Management System API",
            "version": "1.0.0",
            "docs": "/docs",
            "redoc": "/redoc"
        }
    }


@app.get("/health")
async def health_check():
    return {
        "success": True,
        "data": {
            "status": "healthy",
            "service": "TMS API"
        }
    }


@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return {
        "success": False,
        "error": exc.detail,
        "status_code": exc.status_code
    }


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    return {
        "success": False,
        "error": "Internal server error",
        "status_code": 500
    }


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
