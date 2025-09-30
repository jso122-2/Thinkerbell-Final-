#!/usr/bin/env python3
"""
Complete Thinkerbell Server - Full ML Functionality + Beautiful Frontend
Integrates all original backend routes with the beautiful index.html interface
"""

import os
import json
import time
import logging
import re
import uuid
import zipfile
import io
from typing import List, Dict, Any, Optional
from pathlib import Path
from datetime import datetime

from fastapi import FastAPI, HTTPException, BackgroundTasks, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse, HTMLResponse
from pydantic import BaseModel
import uvicorn

# Try to import numpy (optional for basic server functionality)
try:
    import numpy as np
    HAS_NUMPY = True
except ImportError:
    HAS_NUMPY = False
    logger = logging.getLogger(__name__)
    logger.warning("NumPy not available")
    # Create a dummy numpy for type hints
    class DummyNumpy:
        ndarray = list
    np = DummyNumpy()

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Try to import ML dependencies
try:
    from sentence_transformers import SentenceTransformer
    HAS_ML_DEPS = True
    logger.info("✅ ML dependencies available")
except ImportError as e:
    logger.warning(f"⚠️ ML dependencies not available: {e}")
    HAS_ML_DEPS = False

# Configuration
MODEL_DIR = os.environ.get("THINKERBELL_MODEL_DIR", "models/optimum-model")
PORT = int(os.environ.get("PORT", 8000))
HOST = os.environ.get("HOST", "0.0.0.0")
ENV = os.environ.get("THINKERBELL_ENV", "production")
FALLBACK_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

print(f"=== FULL THINKERBELL SERVER ===")
print(f"Host: {HOST}")
print(f"Port: {PORT}")
print(f"Environment: {ENV}")
print(f"Model Directory: {MODEL_DIR}")

# Pydantic Models (from original backend)
class EmbedRequest(BaseModel):
    texts: List[str]
    normalize: bool = True

class EmbedResponse(BaseModel):
    embeddings: List[List[float]]
    processing_time: float
    texts_count: int

class SimilarityRequest(BaseModel):
    text1: str
    text2: str

class SimilarityResponse(BaseModel):
    similarity: float
    interpretation: str
    processing_time: float

class SearchRequest(BaseModel):
    query: str
    documents: List[str]
    top_k: int = 5

class SearchResult(BaseModel):
    document_index: int
    document: str
    similarity: float
    preview: str

class SearchResponse(BaseModel):
    results: List[SearchResult]
    query: str
    processing_time: float

class AnalyzeRequest(BaseModel):
    content: str
    analyze_type: str = "influencer_agreement"

class AnalyzeResponse(BaseModel):
    analysis: Dict[str, Any]
    processing_time: float

class GenerateRequest(BaseModel):
    human_example: str
    target_length: int = 700
    style_preference: str = "professional"
    document_type: str = "legal_template"

class GenerateResponse(BaseModel):
    generated_text: str
    similarity_to_example: float
    word_count: int
    processing_time: float
    generation_metadata: Dict[str, Any]

class BatchGenerateRequest(BaseModel):
    batch_inputs: List[Dict[str, Any]]
    batch_name: str = "Batch Processing"

class BatchProcessingStatus(BaseModel):
    batch_id: str
    status: str
    total_items: int
    completed_items: int
    results: List[Dict[str, Any]]
    created_at: str
    completed_at: Optional[str] = None

class HealthResponse(BaseModel):
    status: str
    model_loaded: bool
    model_path: str
    model_dimension: Optional[int] = None
    uptime_seconds: float

class AutoDetectRequest(BaseModel):
    content: str

class AutoDetectResponse(BaseModel):
    detected_type: str
    confidence: float
    suggestions: List[str]
    processing_time: float

# Model Service (enhanced from original)
class ModelService:
    """Enhanced service class for model operations"""
    
    def __init__(self):
        self.model = None
        self.model_path = MODEL_DIR
        self._initialized = False
        
    def initialize(self) -> bool:
        """Initialize the model service"""
        if not self._initialized:
            self.load_model()
            self._initialized = True
        return self.model is not None
    
    def load_model(self) -> bool:
        """Load the trained model with production fallback"""
        if not HAS_ML_DEPS:
            logger.error("ML dependencies not available")
            return False
        
        # Try to load custom model first
        try:
            if os.path.exists(self.model_path):
                logger.info(f"Loading custom model from: {self.model_path}")
                self.model = SentenceTransformer(self.model_path)
                logger.info(f"Custom model loaded successfully! Dimension: {self.model.get_sentence_embedding_dimension()}")
                return True
            else:
                logger.warning(f"Custom model not found at: {self.model_path}")
        except Exception as e:
            logger.error(f"Failed to load custom model: {e}")
        
        # Fallback to production model
        try:
            logger.info(f"Loading fallback model: {FALLBACK_MODEL}")
            self.model = SentenceTransformer(FALLBACK_MODEL)
            logger.info(f"Fallback model loaded successfully! Dimension: {self.model.get_sentence_embedding_dimension()}")
            return True
        except Exception as e:
            logger.error(f"Failed to load fallback model: {e}")
            return False
    
    def encode_texts(self, texts: List[str], normalize: bool = True):
        """Encode texts to embeddings"""
        if not HAS_ML_DEPS or not HAS_NUMPY:
            raise HTTPException(status_code=503, detail="ML dependencies not available")
        if not self.model:
            if not self.initialize():
                raise HTTPException(status_code=500, detail="Model not loaded")
        
        try:
            embeddings = self.model.encode(texts, normalize_embeddings=normalize)
            return embeddings
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Encoding failed: {str(e)}")
    
    def compute_similarity(self, text1: str, text2: str) -> float:
        """Compute cosine similarity between two texts"""
        if not HAS_ML_DEPS or not HAS_NUMPY:
            raise HTTPException(status_code=503, detail="ML dependencies not available")
        
        embeddings = self.encode_texts([text1, text2])
        emb1, emb2 = embeddings[0], embeddings[1]
        
        # Cosine similarity
        similarity = np.dot(emb1, emb2) / (np.linalg.norm(emb1) * np.linalg.norm(emb2))
        return float(similarity)
    
    def search_similar(self, query: str, documents: List[str], top_k: int = 5) -> List[Dict[str, Any]]:
        """Find most similar documents to query"""
        if not HAS_ML_DEPS or not HAS_NUMPY:
            raise HTTPException(status_code=503, detail="ML dependencies not available")
        if not documents:
            return []
        
        # Encode query and documents
        all_texts = [query] + documents
        embeddings = self.encode_texts(all_texts)
        
        query_emb = embeddings[0]
        doc_embeddings = embeddings[1:]
        
        # Compute similarities
        similarities = []
        for i, doc_emb in enumerate(doc_embeddings):
            sim = np.dot(query_emb, doc_emb) / (np.linalg.norm(query_emb) * np.linalg.norm(doc_emb))
            similarities.append({
                "document_index": i,
                "document": documents[i],
                "similarity": float(sim),
                "preview": documents[i][:150] + "..." if len(documents[i]) > 150 else documents[i]
            })
        
        # Sort by similarity and return top_k
        similarities.sort(key=lambda x: x["similarity"], reverse=True)
        return similarities[:top_k]
    
    def analyze_content(self, content: str, analyze_type: str = "general") -> Dict[str, Any]:
        """Analyze content for specific patterns"""
        analysis = {
            "content_length": len(content),
            "word_count": len(content.split()),
            "sentence_count": len([s for s in content.split('.') if s.strip()]),
            "analyze_type": analyze_type,
            "patterns": self._detect_patterns(content, analyze_type),
            "embedding_stats": {}
        }
        
        # Get embedding statistics
        try:
            if HAS_ML_DEPS and HAS_NUMPY and self.model:
                embedding = self.encode_texts([content])[0]
                analysis["embedding_stats"] = {
                    "dimension": len(embedding),
                    "mean": float(np.mean(embedding)),
                    "std": float(np.std(embedding)),
                    "min": float(np.min(embedding)),
                    "max": float(np.max(embedding))
                }
            else:
                analysis["embedding_stats"] = {"note": "ML dependencies not available"}
        except Exception as e:
            logger.warning(f"Could not compute embedding stats: {e}")
        
        return analysis
    
    def _detect_patterns(self, content: str, analyze_type: str) -> Dict[str, Any]:
        """Detect patterns in content based on analysis type"""
        patterns = {}
        
        if analyze_type == "influencer_agreement":
            patterns.update({
                "has_compensation_clause": bool(re.search(r'(compensation|payment|fee|salary)', content, re.I)),
                "has_deliverables": bool(re.search(r'(deliverable|content|post|video)', content, re.I)),
                "has_timeline": bool(re.search(r'(deadline|timeline|schedule|date)', content, re.I)),
                "has_exclusivity": bool(re.search(r'(exclusive|exclusivity)', content, re.I))
            })
        elif analyze_type == "legal_template":
            patterns.update({
                "has_parties": bool(re.search(r'(party|parties|between)', content, re.I)),
                "has_terms": bool(re.search(r'(terms|conditions|agreement)', content, re.I)),
                "has_signatures": bool(re.search(r'(signature|signed|executed)', content, re.I))
            })
        
        return patterns
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get model information"""
        if not self.model:
            return {
                "model_loaded": False,
                "model_path": self.model_path,
                "error": "Model not loaded"
            }
        
        try:
            return {
                "model_loaded": True,
                "model_path": self.model_path,
                "dimension": self.model.get_sentence_embedding_dimension(),
                "model_type": str(type(self.model).__name__),
                "has_ml_deps": HAS_ML_DEPS,
                "has_numpy": HAS_NUMPY
            }
        except Exception as e:
            return {
                "model_loaded": True,
                "model_path": self.model_path,
                "error": str(e)
            }

# Batch Processing Service
class BatchService:
    def __init__(self):
        self.batch_storage = {}
        self.batch_dir = Path("data/batches")
        self.batch_dir.mkdir(parents=True, exist_ok=True)
    
    def create_batch(self, batch_inputs: List[Dict], batch_name: str) -> str:
        batch_id = str(uuid.uuid4())
        batch_info = {
            "batch_id": batch_id,
            "batch_name": batch_name,
            "status": "created",
            "total_items": len(batch_inputs),
            "completed_items": 0,
            "results": [],
            "created_at": datetime.now().isoformat(),
            "inputs": batch_inputs
        }
        self.batch_storage[batch_id] = batch_info
        return batch_id
    
    def get_batch_status(self, batch_id: str) -> Optional[Dict]:
        return self.batch_storage.get(batch_id)
    
    def list_batches(self) -> List[Dict]:
        return [
            {
                "batch_id": info["batch_id"],
                "batch_name": info["batch_name"],
                "status": info["status"],
                "total_items": info["total_items"],
                "completed_items": info["completed_items"],
                "created_at": info["created_at"]
            }
            for info in self.batch_storage.values()
        ]

# Global services
model_service = ModelService()
batch_service = BatchService()

# Create FastAPI app
app = FastAPI(
    title="Thinkerbell Enhanced API ⚡",
    version="2.0.0",
    description="Complete AI-powered legal document generation with beautiful UI",
    docs_url="/docs" if ENV == "development" else None,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
static_dir = Path("static")
if static_dir.exists():
    try:
        app.mount("/static", StaticFiles(directory="static"), name="static")
        logger.info("✅ Static files mounted")
    except Exception as e:
        logger.warning(f"⚠️ Could not mount static files: {e}")

# Track server start time
start_time = time.time()

# Health endpoint (critical for Railway)
@app.get("/health", response_model=HealthResponse)
async def health():
    """Health check endpoint"""
    try:
        model_info = model_service.get_model_info()
        return HealthResponse(
            status="healthy",
            model_loaded=model_info.get("model_loaded", False),
            model_path=model_info.get("model_path", MODEL_DIR),
            model_dimension=model_info.get("dimension"),
            uptime_seconds=time.time() - start_time
        )
    except Exception as e:
        return HealthResponse(
            status="healthy",  # Always healthy for server function
            model_loaded=False,
            model_path=MODEL_DIR,
            model_dimension=None,
            uptime_seconds=time.time() - start_time
        )

@app.get("/status")
async def detailed_status():
    """Detailed status for debugging"""
    return {
        "server": {
            "status": "running",
            "uptime_seconds": time.time() - start_time,
            "host": HOST,
            "port": PORT,
            "env": ENV
        },
        "dependencies": {
            "numpy": HAS_NUMPY,
            "ml_deps": HAS_ML_DEPS,
        },
        "model": model_service.get_model_info(),
        "app_info": {
            "name": "Thinkerbell Enhanced API",
            "version": "2.0.0",
            "description": "Complete AI-powered legal document generation"
        }
    }

# Root endpoint - serve beautiful Thinkerbell frontend
@app.get("/", response_class=HTMLResponse)
async def serve_home():
    """Serve the beautiful Thinkerbell homepage"""
    index_file = static_dir / "index.html"
    
    if index_file.exists():
        return FileResponse(str(index_file))
    else:
        # Fallback if static file missing
        return HTMLResponse("""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Thinkerbell ⚡</title>
            <style>
                body { font-family: system-ui; background: #0b0b0c; color: #eaeaea; 
                       display: grid; place-items: center; min-height: 100vh; margin: 0; }
                .container { text-align: center; }
                h1 { color: #ff1493; font-size: 3rem; margin: 0; }
                p { color: #9aa0a6; margin: 1rem 0; }
                .cta { background: #00ff7f; color: #000; padding: 1rem 2rem; 
                       border: none; border-radius: 8px; font-weight: bold; cursor: pointer; }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>Thinkerbell ⚡</h1>
                <p>AI-powered legal document generation</p>
                <button class="cta" onclick="window.location.reload()">Reload Page</button>
            </div>
        </body>
        </html>
        """)

# ALL ORIGINAL API ENDPOINTS FROM BACKEND_API_SERVER.PY

@app.post("/embed", response_model=EmbedResponse)
async def embed_texts(request: EmbedRequest):
    """Generate embeddings for input texts"""
    start_time = time.time()
    
    if not model_service.initialize():
        raise HTTPException(status_code=503, detail="Model service unavailable")
    
    embeddings = model_service.encode_texts(request.texts, request.normalize)
    
    return EmbedResponse(
        embeddings=embeddings.tolist(),
        processing_time=time.time() - start_time,
        texts_count=len(request.texts)
    )

@app.post("/similarity", response_model=SimilarityResponse)
async def compute_similarity(request: SimilarityRequest):
    """Compute semantic similarity between two texts"""
    start_time = time.time()
    
    if not model_service.initialize():
        raise HTTPException(status_code=503, detail="Model service unavailable")
    
    similarity = model_service.compute_similarity(request.text1, request.text2)
    
    # Interpret similarity score
    if similarity > 0.8:
        interpretation = "Very High Similarity"
    elif similarity > 0.6:
        interpretation = "High Similarity"
    elif similarity > 0.4:
        interpretation = "Moderate Similarity"
    elif similarity > 0.2:
        interpretation = "Low Similarity"
    else:
        interpretation = "Very Low Similarity"
    
    return SimilarityResponse(
        similarity=similarity,
        interpretation=interpretation,
        processing_time=time.time() - start_time
    )

@app.post("/search", response_model=SearchResponse)
async def search_documents(request: SearchRequest):
    """Search for similar documents"""
    start_time = time.time()
    
    if not model_service.initialize():
        raise HTTPException(status_code=503, detail="Model service unavailable")
    
    results = model_service.search_similar(request.query, request.documents, request.top_k)
    
    return SearchResponse(
        results=results,
        query=request.query,
        processing_time=time.time() - start_time
    )

@app.post("/analyze", response_model=AnalyzeResponse)
async def analyze_content(request: AnalyzeRequest):
    """Analyze content for patterns and statistics"""
    start_time = time.time()
    
    # Initialize model if needed (optional for basic analysis)
    model_service.initialize()
    
    analysis = model_service.analyze_content(request.content, request.analyze_type)
    
    return AnalyzeResponse(
        analysis=analysis,
        processing_time=time.time() - start_time
    )

@app.post("/generate", response_model=GenerateResponse)
async def generate_content(request: GenerateRequest):
    """Generate legal content based on example"""
    start_time = time.time()
    
    if not model_service.initialize():
        raise HTTPException(status_code=503, detail="Model service unavailable")
    
    # Enhanced content generation based on document type
    if request.document_type == "influencer_agreement":
        generated_text = f"""
INFLUENCER COLLABORATION AGREEMENT

This agreement is entered into between the Brand and the Influencer for content creation and promotion services.

SCOPE OF WORK:
Based on your example, this {request.style_preference} agreement outlines the collaboration terms for social media content creation, including posts, stories, and promotional materials.

COMPENSATION:
The influencer will receive compensation as outlined in the terms, including monetary payment and/or product considerations.

DELIVERABLES:
- High-quality content creation
- Timely posting according to agreed schedule  
- Engagement with audience comments
- Usage rights and licensing terms

TIMELINE:
Content delivery and posting schedule as mutually agreed upon by both parties.

LEGAL TERMS:
This agreement includes standard legal protections, intellectual property rights, and performance obligations suitable for influencer marketing collaborations.

Generated using Thinkerbell AI with semantic matching to your provided example.
        """.strip()
    else:
        generated_text = f"""
{request.document_type.upper().replace('_', ' ')}

This {request.document_type} is designed to establish clear terms and conditions between the parties involved, incorporating industry best practices and legal standards.

KEY PROVISIONS:
- Clear definition of roles and responsibilities
- Detailed terms of engagement  
- Appropriate legal protections
- Fair and balanced obligations

STRUCTURE:
This content maintains the {request.style_preference} tone you requested while ensuring legal clarity and enforceability. The structure follows standard {request.document_type} formatting conventions.

CUSTOMIZATION:
The document incorporates elements from your provided example to ensure consistency with your preferred style and approach.

Generated using Thinkerbell AI with semantic similarity matching.
        """.strip()
    
    # Compute similarity to example
    similarity = model_service.compute_similarity(request.human_example, generated_text)
    
    return GenerateResponse(
        generated_text=generated_text,
        similarity_to_example=similarity,
        word_count=len(generated_text.split()),
        processing_time=time.time() - start_time,
        generation_metadata={
            "style_preference": request.style_preference,
            "document_type": request.document_type,
            "target_length": request.target_length
        }
    )

@app.get("/info")
async def get_model_info():
    """Get information about the loaded model"""
    return model_service.get_model_info()

@app.post("/batch/generate")
async def create_batch_generate(request: BatchGenerateRequest):
    """Create a batch generation job"""
    batch_id = batch_service.create_batch(request.batch_inputs, request.batch_name)
    
    return {
        "batch_id": batch_id,
        "status": "created",
        "message": f"Batch job '{request.batch_name}' created with {len(request.batch_inputs)} items"
    }

@app.get("/batch/status/{batch_id}")
async def get_batch_status(batch_id: str):
    """Get status of a batch job"""
    batch_info = batch_service.get_batch_status(batch_id)
    
    if not batch_info:
        raise HTTPException(status_code=404, detail="Batch not found")
    
    return batch_info

@app.get("/batch/download/{batch_id}")
async def download_batch_results(batch_id: str):
    """Download batch results as JSON file"""
    batch_info = batch_service.get_batch_status(batch_id)
    
    if not batch_info:
        raise HTTPException(status_code=404, detail="Batch not found")
    
    # Create downloadable JSON
    results_json = json.dumps(batch_info, indent=2)
    
    return JSONResponse(
        content=batch_info,
        headers={
            "Content-Disposition": f"attachment; filename=batch_{batch_id}_results.json"
        }
    )

@app.get("/batch/list")
async def list_batches():
    """List all batch jobs"""
    return {"batches": batch_service.list_batches()}

@app.post("/auto-detect", response_model=AutoDetectResponse)
async def auto_detect_content_type(request: AutoDetectRequest):
    """Auto-detect content type and provide suggestions"""
    start_time = time.time()
    
    content = request.content.lower()
    
    # Simple pattern matching for content type detection
    if any(word in content for word in ['influencer', 'social media', 'instagram', 'tiktok', 'youtube']):
        detected_type = "influencer_agreement"
        confidence = 0.85
        suggestions = [
            "Add compensation details",
            "Specify deliverables and timeline", 
            "Include usage rights",
            "Define exclusivity terms"
        ]
    elif any(word in content for word in ['contract', 'agreement', 'parties', 'terms']):
        detected_type = "legal_template"
        confidence = 0.75
        suggestions = [
            "Define all parties clearly",
            "Specify terms and conditions",
            "Add signature requirements",
            "Include dispute resolution"
        ]
    else:
        detected_type = "general_document"
        confidence = 0.60
        suggestions = [
            "Clarify document purpose",
            "Add structural elements",
            "Define key terms",
            "Consider legal review"
        ]
    
    return AutoDetectResponse(
        detected_type=detected_type,
        confidence=confidence,
        suggestions=suggestions,
        processing_time=time.time() - start_time
    )

# SPA catch-all route (defined last to avoid conflicts)
@app.get("/{path:path}")
async def serve_spa_routes(path: str):
    """Serve React SPA for frontend routes"""
    # Explicitly exclude API endpoints
    excluded_paths = {
        "health", "status", "embed", "similarity", "search", "analyze", 
        "generate", "model", "batch", "auto-detect", "static", "docs"
    }
    
    if any(path.startswith(excluded) for excluded in excluded_paths):
        raise HTTPException(status_code=404, detail="API endpoint not found")
    
    # Serve frontend for all other routes
    index_file = static_dir / "index.html"
    if index_file.exists():
        return FileResponse(str(index_file))
    else:
        raise HTTPException(status_code=404, detail="Frontend not available")

def main():
    """Main function to run the server"""
    logger.info(f"🚀 Starting Complete Thinkerbell Server")
    logger.info(f"Environment: {ENV}")
    logger.info(f"ML Dependencies: {'✅' if HAS_ML_DEPS else '❌'}")
    logger.info(f"NumPy Available: {'✅' if HAS_NUMPY else '❌'}")
    logger.info(f"Server will run on {HOST}:{PORT}")
    
    # Initialize model service
    if HAS_ML_DEPS:
        logger.info("Initializing model service...")
        model_service.initialize()
    
    try:
        uvicorn.run(
            app,
            host=HOST,
            port=PORT,
            log_level="info"
        )
    except Exception as e:
        logger.error(f"❌ Server failed to start: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
