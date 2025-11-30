"""
FastAPI Main Application
========================

Real-time image processing API for eScriptorium.

Features:
- REST API endpoints for image processing
- WebSocket support for real-time feedback
- Async processing for better performance

Usage:
    uvicorn fastapi_app.main:app --reload --port 8001
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI application
app = FastAPI(
    title="eScriptorium FastAPI",
    description="Real-time image processing API for manuscript analysis",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json"
)

# CORS Configuration
# TODO: Update origins in production
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:8000",  # Django development
        "http://localhost:3000",  # Frontend development
        "http://127.0.0.1:8000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Import routers
from .routers import images, websocket
app.include_router(images.router, prefix="/api/images", tags=["images"])
app.include_router(websocket.router, tags=["websocket"])  # WebSocket router (Day 4)


@app.get("/")
async def root():
    """Root endpoint - API information"""
    return {
        "message": "eScriptorium FastAPI is running",
        "version": "1.1.0",
        "status": "operational",
        "features": ["REST API", "WebSocket Real-time"],
        "endpoints": {
            "docs": "/api/docs",
            "health": "/health",
            "images": "/api/images/*",
            "websocket_process": "/ws/process",
            "websocket_monitor": "/ws/monitor"
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    from .routers.websocket import manager
    return {
        "status": "healthy",
        "service": "fastapi",
        "version": "1.1.0",
        "websocket_connections": manager.get_connection_count()
    }


@app.get("/api/info")
async def api_info():
    """Get API capabilities and available endpoints"""
    return {
        "service": "eScriptorium FastAPI",
        "version": "1.0.0",
        "capabilities": [
            "Image binarization (Otsu, Adaptive)",
            "Noise reduction",
            "Image deskewing",
            "Contrast enhancement",
            "Auto manuscript processing",
            "Real-time WebSocket processing"
        ],
        "endpoints": {
            "rest": {
                "binarize": "POST /api/images/binarize",
                "denoise": "POST /api/images/denoise",
                "deskew": "POST /api/images/deskew",
                "enhance": "POST /api/images/enhance",
                "auto_process": "POST /api/images/auto-process"
            },
            "websocket": {
                "process": "WS /ws/process"
            }
        }
    }


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler"""
    logger.error(f"Global exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "message": str(exc),
            "type": type(exc).__name__
        }
    )


# Startup event
@app.on_event("startup")
async def startup_event():
    """Run on application startup"""
    logger.info("FastAPI application starting up...")
    logger.info("Image processing service initialized")
    logger.info("REST API endpoints registered:")
    logger.info("  - POST /api/images/binarize")
    logger.info("  - POST /api/images/denoise")
    logger.info("  - POST /api/images/deskew")
    logger.info("  - POST /api/images/enhance")
    logger.info("  - POST /api/images/auto-process")
    logger.info("API documentation available at /api/docs")


# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    """Run on application shutdown"""
    logger.info("FastAPI application shutting down...")
    logger.info("Closing connections...")


if __name__ == "__main__":
    import uvicorn
    # Security: Bind to localhost only for development
    # For production, use proper deployment (gunicorn/nginx) instead of this direct run
    uvicorn.run(
        "main:app",
        host="127.0.0.1",  # localhost only - not exposed to network
        port=8001,
        reload=True,
        log_level="info"
    )
