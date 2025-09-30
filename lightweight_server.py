#!/usr/bin/env python3
"""
Lightweight Thinkerbell Server for Railway Deployment
Optimized to stay under 5.5GB Docker image limit
"""

import os
import json
import time
import logging
from typing import List, Dict, Any, Optional
from pathlib import Path
from datetime import datetime, timedelta

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel
import uvicorn

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration
PORT = int(os.environ.get("PORT", 8000))
HOST = os.environ.get("HOST", "0.0.0.0")
ENV = os.environ.get("THINKERBELL_ENV", "production")
STATIC_DIR = Path("static")

# Try to import ML dependencies (graceful fallback if not available)
try:
    import torch
    import numpy as np
    HAS_TORCH = True
    logger.info("✅ PyTorch available")
except ImportError:
    HAS_TORCH = False
    logger.warning("⚠️ PyTorch not available - using mock ML responses")

try:
    from transformers import AutoTokenizer, AutoModel
    HAS_TRANSFORMERS = True
    logger.info("✅ Transformers available")
except ImportError:
    HAS_TRANSFORMERS = False
    logger.warning("⚠️ Transformers not available - using mock ML responses")

# Pydantic Models
class EmbedRequest(BaseModel):
    texts: List[str]
    normalize: bool = True

class SimilarityRequest(BaseModel):
    text1: str
    text2: str

class SearchRequest(BaseModel):
    query: str
    documents: List[str]
    top_k: int = 5

class GenerateRequest(BaseModel):
    human_example: str
    target_length: int = 700
    style_preference: str = "professional"
    document_type: str = "legal_template"

class HealthResponse(BaseModel):
    status: str
    model_loaded: bool
    ml_dependencies: bool
    uptime: str

# Lightweight Model Service
class LightweightModelService:
    """Lightweight model service with graceful ML fallbacks"""
    
    def __init__(self):
        self.model = None
        self.tokenizer = None
        self.model_loaded = False
        self._try_load_model()
    
    def _try_load_model(self):
        """Try to load a lightweight model if dependencies are available"""
        if not HAS_TORCH or not HAS_TRANSFORMERS:
            logger.info("🔄 ML dependencies not available - using mock responses")
            return
        
        try:
            # Try to load a very lightweight model
            model_name = "sentence-transformers/all-MiniLM-L6-v2"
            logger.info(f"🔄 Attempting to load lightweight model: {model_name}")
            
            # This would normally load the model, but we'll skip for size constraints
            # self.tokenizer = AutoTokenizer.from_pretrained(model_name)
            # self.model = AutoModel.from_pretrained(model_name)
            # self.model_loaded = True
            
            logger.info("⚠️ Skipping model loading to keep image size under 5.5GB")
            
        except Exception as e:
            logger.error(f"❌ Failed to load model: {e}")
    
    def encode_texts(self, texts: List[str], normalize: bool = True) -> List[List[float]]:
        """Generate mock embeddings for texts"""
        if self.model_loaded and HAS_TORCH:
            # Real model inference would go here
            pass
        
        # Mock embeddings (384 dimensions for MiniLM)
        import random
        embeddings = []
        for text in texts:
            # Generate consistent mock embeddings based on text hash
            random.seed(hash(text) % 2**32)
            embedding = [random.uniform(-1, 1) for _ in range(384)]
            embeddings.append(embedding)
        
        return embeddings
    
    def compute_similarity(self, text1: str, text2: str) -> float:
        """Compute mock similarity between texts"""
        # Simple mock similarity based on text length and common words
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())
        
        if not words1 or not words2:
            return 0.0
        
        common_words = len(words1.intersection(words2))
        total_words = len(words1.union(words2))
        
        similarity = common_words / total_words if total_words > 0 else 0.0
        return min(similarity + 0.2, 1.0)  # Add base similarity
    
    def search_similar(self, query: str, documents: List[str], top_k: int = 5) -> List[Dict[str, Any]]:
        """Mock document search"""
        results = []
        for doc in documents:
            score = self.compute_similarity(query, doc)
            results.append({"document": doc, "score": score})
        
        # Sort by score and return top_k
        results.sort(key=lambda x: x["score"], reverse=True)
        return results[:top_k]
    
    def generate_content(self, human_example: str, target_length: int = 700, 
                        style_preference: str = "professional", 
                        document_type: str = "legal_template") -> str:
        """Generate enhanced legal content based on example"""
        
        # Enhanced template-based generation
        base_template = f"""
ENHANCED {document_type.upper().replace('_', ' ')}

This agreement is based on the provided example and enhanced for professional use.

ORIGINAL CONTEXT:
{human_example[:200]}{'...' if len(human_example) > 200 else ''}

ENHANCED LEGAL FRAMEWORK:

1. PARTIES AND DEFINITIONS
This agreement establishes the relationship between the parties as outlined in the original example, with enhanced legal protections and clarity.

2. SCOPE OF WORK AND DELIVERABLES
Based on the described requirements, the scope includes all activities and deliverables mentioned in the original context, with additional professional standards and quality assurance measures.

3. COMPENSATION AND PAYMENT TERMS
Payment structure follows industry standards with clear milestones, invoicing procedures, and dispute resolution mechanisms.

4. INTELLECTUAL PROPERTY RIGHTS
Comprehensive IP protection covering all created content, with clear ownership attribution and usage rights as applicable to this type of agreement.

5. CONFIDENTIALITY AND NON-DISCLOSURE
Standard confidentiality provisions protecting sensitive information shared between parties during the course of this engagement.

6. TERMINATION AND DISPUTE RESOLUTION
Clear termination procedures and dispute resolution mechanisms including mediation and arbitration options.

7. COMPLIANCE AND LEGAL REQUIREMENTS
Ensures compliance with all applicable laws, regulations, and industry standards relevant to this type of professional engagement.

This enhanced template provides a solid legal foundation while maintaining the core intent and requirements from your original example. All terms should be reviewed by qualified legal counsel before execution.

Generated with Thinkerbell Enhanced Legal AI - Professional Document Generation System
Target Style: {style_preference} | Document Type: {document_type} | Target Length: {target_length} words
"""
        
        # Adjust length to target
        words = base_template.split()
        if len(words) > target_length:
            words = words[:target_length]
            base_template = ' '.join(words) + "..."
        elif len(words) < target_length:
            # Add more content to reach target length
            additional_content = """

ADDITIONAL PROVISIONS:

8. PERFORMANCE STANDARDS
All work performed under this agreement shall meet professional industry standards and best practices.

9. COMMUNICATION PROTOCOLS
Regular communication schedules and reporting requirements to ensure project success.

10. MODIFICATION AND AMENDMENTS
Any changes to this agreement must be made in writing and signed by all parties.

11. GOVERNING LAW
This agreement shall be governed by applicable local and federal laws.

12. ENTIRE AGREEMENT
This document represents the complete agreement between parties and supersedes all prior negotiations."""
            
            base_template += additional_content
        
        return base_template

# Initialize services
model_service = LightweightModelService()
start_time = time.time()

# FastAPI App
app = FastAPI(
    title="Thinkerbell Lightweight API",
    version="2.0.0-lightweight",
    description="Lightweight Thinkerbell API optimized for Railway deployment",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files if available
if STATIC_DIR.exists():
    try:
        app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
        logger.info(f"✅ Static files mounted from {STATIC_DIR}")
    except Exception as e:
        logger.warning(f"⚠️ Could not mount static files: {e}")

# Routes
@app.get("/")
async def serve_root():
    """Serve the Thinkerbell frontend"""
    index_file = STATIC_DIR / "index.html"
    if index_file.exists():
        return FileResponse(index_file)
    else:
        return {
            "message": "Thinkerbell Lightweight API",
            "version": "2.0.0-lightweight",
            "status": "operational",
            "note": "Optimized for Railway deployment under 5.5GB limit"
        }

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    current_time = time.time()
    uptime_seconds = current_time - start_time
    uptime_str = str(timedelta(seconds=int(uptime_seconds)))
    
    return HealthResponse(
        status="healthy",
        model_loaded=model_service.model_loaded,
        ml_dependencies=HAS_TORCH and HAS_TRANSFORMERS,
        uptime=uptime_str
    )

@app.post("/embed")
async def embed_texts(request: EmbedRequest):
    """Generate embeddings for texts"""
    embeddings = model_service.encode_texts(request.texts, request.normalize)
    return {"embeddings": embeddings}

@app.post("/similarity")
async def compute_similarity(request: SimilarityRequest):
    """Compute similarity between two texts"""
    similarity = model_service.compute_similarity(request.text1, request.text2)
    return {"similarity": similarity}

@app.post("/search")
async def search_similar_documents(request: SearchRequest):
    """Search for similar documents"""
    results = model_service.search_similar(request.query, request.documents, request.top_k)
    return {"query": request.query, "results": results}

@app.post("/generate")
async def generate_content(request: GenerateRequest):
    """Generate enhanced legal content"""
    generated_text = model_service.generate_content(
        request.human_example,
        request.target_length,
        request.style_preference,
        request.document_type
    )
    return {"generated_text": generated_text}

@app.post("/auto-detect")
async def auto_detect_content_type(request: dict):
    """Auto-detect content type and parameters"""
    content = request.get("content", "") or request.get("text", "")
    
    if not content:
        raise HTTPException(status_code=400, detail="No content provided")
    
    # Simple rule-based auto-detection
    content_lower = content.lower()
    word_count = len(content.split())
    
    # Detect document type
    detected_type = "legal_template"
    confidence = 0.7
    
    if "influencer" in content_lower or "instagram" in content_lower or "social media" in content_lower:
        detected_type = "influencer_agreement"
        confidence = 0.9
    elif "content" in content_lower and ("article" in content_lower or "blog" in content_lower):
        detected_type = "content_creation"
        confidence = 0.8
    elif "brand" in content_lower and "partnership" in content_lower:
        detected_type = "brand_partnership"
        confidence = 0.8
    elif "marketing" in content_lower or "advertising" in content_lower:
        detected_type = "marketing_agreement"
        confidence = 0.8
    
    # Detect style preference
    style_preference = "professional"
    if "shall" in content_lower or "hereby" in content_lower or "whereas" in content_lower:
        style_preference = "formal"
    elif "detailed" in content_lower or "comprehensive" in content_lower:
        style_preference = "detailed"
    elif "business" in content_lower or "company" in content_lower:
        style_preference = "business"
    
    # Detect target length based on input length
    target_length = 700
    if word_count < 50:
        target_length = 500
    elif word_count > 200:
        target_length = 1200
    elif word_count > 100:
        target_length = 1000
    
    return {
        "detected_type": detected_type,
        "confidence": confidence,
        "target_length": target_length,
        "style_preference": style_preference,
        "document_type": detected_type,
        "confidence_scores": {
            "overall": confidence,
            "document_type": confidence,
            "style": 0.8,
            "length": 0.7
        },
        "reasoning": {
            "target_length": f"Based on input length ({word_count} words)",
            "style_preference": "Detected from content analysis",
            "document_type": "Inferred from keywords and context"
        }
    }

@app.post("/analyze")
async def analyze_content(request: dict):
    """Analyze content for specific patterns"""
    content = request.get("content", "")
    analyze_type = request.get("analyze_type", "influencer_agreement")
    
    if not content:
        raise HTTPException(status_code=400, detail="No content provided")
    
    analysis_results = {"type": analyze_type, "findings": []}
    
    if analyze_type == "influencer_agreement":
        keywords = {
            "payment_terms": ["payment", "fee", "compensation", "remuneration"],
            "deliverables": ["deliverable", "post", "story", "content", "campaign"],
            "exclusivity": ["exclusive", "exclusivity", "sole"],
            "termination": ["terminate", "termination", "cancel"],
            "intellectual_property": ["IP", "intellectual property", "copyright", "ownership"]
        }
        
        found_keywords = {k: [] for k in keywords}
        for category, kws in keywords.items():
            for kw in kws:
                if kw.lower() in content.lower():
                    found_keywords[category].append(kw)
        
        for category, found in found_keywords.items():
            if found:
                analysis_results["findings"].append(f"Found {category} related terms: {', '.join(found)}")
            else:
                analysis_results["findings"].append(f"No {category} related terms found.")
    else:
        analysis_results["findings"].append(f"Analysis type '{analyze_type}' not supported.")
    
    return {"analysis": analysis_results}

@app.get("/info")
async def get_info():
    """Get system information"""
    return {
        "app_name": "Thinkerbell Lightweight API",
        "version": "2.0.0-lightweight",
        "environment": ENV,
        "ml_dependencies": {
            "torch": HAS_TORCH,
            "transformers": HAS_TRANSFORMERS,
            "model_loaded": model_service.model_loaded
        },
        "optimization": "Designed for Railway 5.5GB limit",
        "features": [
            "Mock ML responses for development",
            "Template-based content generation", 
            "Lightweight dependencies",
            "Full API compatibility",
            "Auto-detection support",
            "Content analysis"
        ]
    }

# Catch-all route for SPA
@app.get("/{path:path}")
async def serve_spa_routes(path: str):
    """Serve React SPA for frontend routes"""
    excluded_paths = ["health", "embed", "similarity", "search", "generate", "info"]
    
    if any(path.startswith(ep) for ep in excluded_paths):
        raise HTTPException(status_code=404, detail="API endpoint not found")
    
    index_file = STATIC_DIR / "index.html"
    if index_file.exists():
        return FileResponse(index_file)
    else:
        raise HTTPException(status_code=404, detail="Frontend not available")

if __name__ == "__main__":
    logger.info(f"🚀 Starting Thinkerbell Lightweight Server...")
    logger.info(f"📊 Environment: {ENV}")
    logger.info(f"🌐 Server: {HOST}:{PORT}")
    logger.info(f"🔧 ML Dependencies: torch={HAS_TORCH}, transformers={HAS_TRANSFORMERS}")
    
    uvicorn.run(
        app,
        host=HOST,
        port=PORT,
        reload=False,
        log_level="info"
    )
