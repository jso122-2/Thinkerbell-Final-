"""
Business logic and service layer
"""

# Use lazy imports to avoid circular dependencies
def get_model_service():
    from .model_service import model_service
    return model_service

def get_batch_service():
    from .batch_service import batch_service
    return batch_service

__all__ = ["get_model_service", "get_batch_service"]
