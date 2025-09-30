"""
API route modules
"""

from .health import router as health_router
from .ml_endpoints import router as ml_router
from .batch_endpoints import router as batch_router
from .frontend import router as frontend_router

__all__ = ["health_router", "ml_router", "batch_router", "frontend_router"]
