"""
API route modules
"""

# Import routers explicitly to avoid circular imports
def get_health_router():
    from .health import router
    return router

def get_ml_router():
    from .ml_endpoints import router
    return router

def get_batch_router():
    from .batch_endpoints import router
    return router

def get_frontend_router():
    from .frontend import router
    return router

__all__ = [
    "get_health_router", 
    "get_ml_router", 
    "get_batch_router", 
    "get_frontend_router"
]
