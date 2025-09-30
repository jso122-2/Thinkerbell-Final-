"""
Main FastAPI application with modular architecture
"""

import logging
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from .core.config import settings
from .routes import get_health_router, get_ml_router, get_batch_router, get_frontend_router

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def create_app() -> FastAPI:
    """Create and configure the FastAPI application"""
    
    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.VERSION,
        description=settings.DESCRIPTION,
        docs_url="/docs" if settings.DEBUG else None,
        redoc_url="/redoc" if settings.DEBUG else None,
    )
    
    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Configure appropriately for production
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Mount static files if they exist
    if settings.STATIC_DIR.exists():
        try:
            app.mount("/assets", StaticFiles(directory=settings.STATIC_DIR / "assets"), name="assets")
            app.mount("/static", StaticFiles(directory=settings.STATIC_DIR), name="static")
            logger.info("Static files mounted successfully")
        except Exception as e:
            logger.warning(f"Could not mount static files: {e}")
    
    # Include routers in order of priority
    # Health checks first (most important for Railway)
    app.include_router(get_health_router(), tags=["Health"])
    
    # ML endpoints
    app.include_router(get_ml_router(), tags=["Machine Learning"])
    
    # Batch processing
    app.include_router(get_batch_router(), tags=["Batch Processing"])
    
    # Frontend routes LAST (catch-all routes)
    app.include_router(get_frontend_router(), tags=["Frontend"])
    
    return app

# Create the app instance
app = create_app()

def main():
    """Main function to run the server"""
    logger.info(f"Starting {settings.APP_NAME} v{settings.VERSION}")
    logger.info(f"Environment: {settings.ENV}")
    logger.info(f"Server will run on {settings.HOST}:{settings.PORT}")
    
    # Always start the server - modular design handles missing dependencies gracefully
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.RELOAD,
        log_level="info",
        workers=settings.WEB_CONCURRENCY if not settings.RELOAD else 1
    )

if __name__ == "__main__":
    main()
