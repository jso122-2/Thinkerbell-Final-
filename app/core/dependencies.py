"""
Dependency management and optional imports
"""

import logging

logger = logging.getLogger(__name__)

# Try to import numpy (optional for basic server functionality)
try:
    import numpy as np
    HAS_NUMPY = True
except ImportError:
    HAS_NUMPY = False
    logger.warning("NumPy not available")
    # Create a dummy numpy for type hints
    class DummyNumpy:
        ndarray = list
    np = DummyNumpy()

# Try to import ML dependencies
try:
    from sentence_transformers import SentenceTransformer
    HAS_ML_DEPS = True
    logger.info("ML dependencies available")
except ImportError as e:
    logger.warning(f"ML dependencies not available: {e}")
    HAS_ML_DEPS = False

# Dependency status
DEPENDENCIES = {
    "numpy": HAS_NUMPY,
    "ml_deps": HAS_ML_DEPS,
}

def get_dependency_status():
    """Get current dependency status"""
    return DEPENDENCIES.copy()
