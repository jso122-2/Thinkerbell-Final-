#!/usr/bin/env python3
"""
PRODUCTION SERVER - EXACT COPY OF WORKING DEVELOPMENT SETUP
Critical: Client paying for optimum model performance
"""

import os
import sys
import logging
from pathlib import Path

# Force the model path to where we know the optimum model is
os.environ["THINKERBELL_MODEL_DIR"] = "models/optimum-model"

# Import the working full server
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Verify model files exist
model_dir = Path("models/optimum-model")
if model_dir.exists():
    model_files = list(model_dir.glob("*"))
    logger.info(f"✅ Model directory exists with {len(model_files)} files")
    for f in model_files[:5]:  # Show first 5 files
        logger.info(f"   - {f.name}")
else:
    logger.error(f"❌ Model directory not found: {model_dir}")
    # Try alternative path
    alt_dir = Path("app/model/optimum-model")
    if alt_dir.exists():
        logger.info(f"✅ Found model at alternative path: {alt_dir}")
        os.environ["THINKERBELL_MODEL_DIR"] = "app/model/optimum-model"
    else:
        logger.error(f"❌ Alternative path also not found: {alt_dir}")

# Import and run the full server
if __name__ == "__main__":
    logger.info("🚀 Starting PRODUCTION server with optimum model...")
    logger.info(f"📂 Model directory: {os.environ.get('THINKERBELL_MODEL_DIR')}")
    
    # Import the full server code
    from full_thinkerbell_server import app, logger as server_logger
    import uvicorn
    
    # Get port from environment
    port = int(os.environ.get("PORT", 8000))
    host = os.environ.get("HOST", "0.0.0.0")
    
    logger.info(f"🌐 Server starting on {host}:{port}")
    
    uvicorn.run(
        app,
        host=host,
        port=port,
        reload=False,
        log_level="info"
    )
