"""
PM Automation System - Main FastAPI Application
Handles JIRA webhooks and orchestrates automation rules
"""

from fastapi import FastAPI, HTTPException, Request, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging
from datetime import datetime

from app.webhooks import router as webhooks_router
from app.api.routes import router as api_router
from app.db.database import init_db

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize on startup, cleanup on shutdown"""
    logger.info("🚀 PM Automation System starting up...")

    # Initialize database
    await init_db()
    logger.info("✅ Database initialized")

    yield

    logger.info("👋 Shutting down PM Automation System")


app = FastAPI(
    title="PM Automation System",
    description="End-to-end program management automation with governance guardrails",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware for dashboard access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure this properly in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(webhooks_router, prefix="/webhooks", tags=["webhooks"])
app.include_router(api_router, prefix="/api", tags=["api"])


@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "operational",
        "service": "PM Automation System",
        "version": "1.0.0",
        "timestamp": datetime.utcnow().isoformat()
    }


@app.get("/health")
async def health_check():
    """Detailed health check for monitoring"""
    return {
        "status": "healthy",
        "database": "connected",
        "timestamp": datetime.utcnow().isoformat()
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
