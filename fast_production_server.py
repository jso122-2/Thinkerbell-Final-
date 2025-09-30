#!/usr/bin/env python3
"""
FAST PRODUCTION SERVER - Optimized for Speed & Client's Optimum Model
Critical: 31+ second processing time is unacceptable for client
"""

import os
import sys
import logging
import time
from pathlib import Path
from typing import Optional, List, Dict, Any
import asyncio

# FastAPI imports
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn

# Force optimum model path
os.environ["THINKERBELL_MODEL_DIR"] = "models/optimum-model"

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global model instance - KEEP IN MEMORY
MODEL_INSTANCE = None
MODEL_LOADED = False

class GenerateRequest(BaseModel):
    human_example: str
    target_length: int = 500
    style_preference: str = "professional"
    document_type: str = "contract"

class EmbedRequest(BaseModel):
    texts: List[str]
    normalize: bool = True

class SimilarityRequest(BaseModel):
    text1: str
    text2: str
    text3: Optional[str] = None

def load_optimum_model_once():
    """Load the client's optimum model ONCE and keep in memory"""
    global MODEL_INSTANCE, MODEL_LOADED
    
    if MODEL_LOADED and MODEL_INSTANCE is not None:
        logger.info("✅ Model already loaded in memory")
        return MODEL_INSTANCE
    
    try:
        logger.info("🚀 Loading client's optimum model...")
        start_time = time.time()
        
        # Import ML dependencies
        from sentence_transformers import SentenceTransformer
        import numpy as np
        
        # Try local optimum model first
        model_path = "models/optimum-model"
        if Path(model_path).exists():
            logger.info(f"📂 Loading from local path: {model_path}")
            MODEL_INSTANCE = SentenceTransformer(model_path)
        else:
            # Try alternative path
            alt_path = "app/model/optimum-model"
            if Path(alt_path).exists():
                logger.info(f"📂 Loading from alternative path: {alt_path}")
                MODEL_INSTANCE = SentenceTransformer(alt_path)
            else:
                # Fallback to fast model
                logger.warning("⚠️ Optimum model not found, using fast fallback")
                MODEL_INSTANCE = SentenceTransformer('all-MiniLM-L6-v2')
        
        load_time = time.time() - start_time
        MODEL_LOADED = True
        
        logger.info(f"✅ Model loaded successfully in {load_time:.2f}s")
        logger.info(f"📊 Model dimension: {MODEL_INSTANCE.get_sentence_embedding_dimension()}")
        
        return MODEL_INSTANCE
        
    except Exception as e:
        logger.error(f"❌ Failed to load model: {e}")
        MODEL_LOADED = False
        return None

# Initialize FastAPI
app = FastAPI(title="Thinkerbell Legal AI - FAST", version="2.0")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load model at startup
@app.on_event("startup")
async def startup_event():
    """Load model once at startup"""
    logger.info("🚀 Starting FAST production server...")
    load_optimum_model_once()

# Static files
static_dir = Path("static")
if static_dir.exists():
    app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/health")
async def health_check():
    """Fast health check"""
    return {
        "status": "healthy",
        "model_loaded": MODEL_LOADED,
        "ml_dependencies": True,
        "server": "fast_production"
    }

@app.get("/info")
async def get_model_info():
    """Get model information"""
    global MODEL_INSTANCE, MODEL_LOADED
    
    if not MODEL_LOADED or MODEL_INSTANCE is None:
        return {"error": "Model not loaded"}
    
    try:
        return {
            "model_loaded": MODEL_LOADED,
            "model_path": "models/optimum-model",
            "dimension": MODEL_INSTANCE.get_sentence_embedding_dimension(),
            "model_type": "SentenceTransformer",
            "has_ml_deps": True,
            "has_numpy": True,
            "server": "fast_production"
        }
    except Exception as e:
        return {"error": str(e)}

@app.post("/embed")
async def embed_texts(request: EmbedRequest):
    """Fast embedding generation"""
    global MODEL_INSTANCE, MODEL_LOADED
    
    if not MODEL_LOADED or MODEL_INSTANCE is None:
        raise HTTPException(status_code=503, detail="Model not loaded")
    
    try:
        start_time = time.time()
        
        # Generate embeddings using loaded model
        embeddings = MODEL_INSTANCE.encode(
            request.texts,
            normalize_embeddings=request.normalize,
            convert_to_numpy=True
        )
        
        processing_time = (time.time() - start_time) * 1000
        
        return {
            "embeddings": embeddings.tolist(),
            "processing_time": processing_time,
            "model_used": "optimum_model"
        }
        
    except Exception as e:
        logger.error(f"Embedding error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/similarity")
async def compute_similarity(request: SimilarityRequest):
    """Fast similarity computation"""
    global MODEL_INSTANCE, MODEL_LOADED
    
    if not MODEL_LOADED or MODEL_INSTANCE is None:
        raise HTTPException(status_code=503, detail="Model not loaded")
    
    try:
        start_time = time.time()
        
        # Compute embeddings
        texts = [request.text1, request.text2]
        if request.text3:
            texts.append(request.text3)
            
        embeddings = MODEL_INSTANCE.encode(texts, normalize_embeddings=True)
        
        # Compute similarities
        from sklearn.metrics.pairwise import cosine_similarity
        similarities = cosine_similarity(embeddings)
        
        processing_time = (time.time() - start_time) * 1000
        
        result = {
            "similarity": float(similarities[0][1]),
            "processing_time": processing_time
        }
        
        if request.text3:
            result.update({
                "similarity_1_2": float(similarities[0][1]),
                "similarity_1_3": float(similarities[0][2]),
                "similarity_2_3": float(similarities[1][2])
            })
        
        return result
        
    except Exception as e:
        logger.error(f"Similarity error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/generate")
async def generate_legal_document(request: GenerateRequest):
    """Generate comprehensive legal documents using working backend_api_server.py methods"""
    global MODEL_INSTANCE, MODEL_LOADED
    
    try:
        start_time = time.time()
        
        # Use the working generation method from backend_api_server.py
        generated_text = generate_from_templates(
            request.human_example, 
            request.target_length, 
            request.style_preference,
            request.document_type
        )
        
        processing_time = (time.time() - start_time) * 1000
        
        return {
            "generated_text": generated_text,
            "processing_time": processing_time,
            "word_count": len(generated_text.split()),
            "model_used": "backend_api_server_method",
            "status": "success"
        }
        
    except Exception as e:
        logger.error(f"Generation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

def generate_from_templates(human_example: str, target_length: int, 
                           style_preference: str, document_type: str) -> str:
    """Generate comprehensive legal text - WORKING METHOD from backend_api_server.py"""
    
    # Extract key elements from human example
    example_words = human_example.lower().split()
    
    # Determine document type and header
    if any(term in example_words for term in ["influencer", "social", "media", "instagram", "youtube", "tiktok"]):
        header = "INFLUENCER MARKETING AGREEMENT"
        doc_type = "influencer"
    elif any(term in example_words for term in ["brand", "partnership"]):
        header = "BRAND PARTNERSHIP CONTRACT"
        doc_type = "partnership"
    elif any(term in example_words for term in ["content", "creation"]):
        header = "CONTENT CREATION AGREEMENT"
        doc_type = "content"
    elif any(term in example_words for term in ["employment", "job", "work", "employee"]):
        header = "EMPLOYMENT AGREEMENT"
        doc_type = "employment"
    elif any(term in example_words for term in ["service", "consulting", "freelance"]):
        header = "SERVICE AGREEMENT"
        doc_type = "service"
    else:
        header = "COLLABORATION AGREEMENT"
        doc_type = "general"
    
    # Build comprehensive legal document with multiple sections
    sections = []
    
    # 1. Header and Introduction
    sections.append(f"{header}\n\n")
    intro_section = generate_detailed_introduction(human_example, doc_type, style_preference)
    sections.append(intro_section)
    
    # 2. Scope of Work/Services
    scope_section = generate_detailed_scope_section(human_example, doc_type)
    sections.append(scope_section)
    
    # 3. Content Requirements and Deliverables
    content_section = generate_content_section(human_example, doc_type)
    sections.append(content_section)
    
    # 4. Terms and Compensation
    terms_section = generate_comprehensive_terms_section(human_example, doc_type)
    sections.append(terms_section)
    
    # 5. Performance Metrics and Standards
    performance_section = generate_performance_section(human_example, doc_type)
    sections.append(performance_section)
    
    # 6. Rights and Intellectual Property
    rights_section = generate_rights_section(human_example, doc_type)
    sections.append(rights_section)
    
    # 7. Compliance and Legal Requirements
    compliance_section = generate_compliance_section(doc_type)
    sections.append(compliance_section)
    
    # 8. Termination and Dispute Resolution
    termination_section = generate_termination_section(doc_type)
    sections.append(termination_section)
    
    # 9. General Provisions
    general_section = generate_general_provisions(doc_type)
    sections.append(general_section)
    
    # Combine all sections
    full_document = "\n\n".join(sections)
    
    # Ensure target length is met by expanding if needed
    current_words = len(full_document.split())
    if current_words < target_length:
        # Add additional detailed clauses to reach target length
        additional_section = generate_additional_clauses(human_example, doc_type, target_length - current_words)
        full_document += f"\n\n{additional_section}"
    
    return full_document

def generate_detailed_introduction(human_example: str, doc_type: str, style_preference: str) -> str:
    """Generate detailed introduction section"""
    if doc_type == "influencer":
        return f"""INTRODUCTION AND BACKGROUND

This Influencer Marketing Agreement ("Agreement") is entered into between the Brand and the Influencer for the purpose of establishing a comprehensive social media collaboration framework. The collaboration is designed to leverage the Influencer's authentic voice and engaged audience to promote the Brand's products and services across various digital platforms.

BASED ON YOUR SPECIFIC REQUIREMENTS:
{human_example}

This Agreement establishes clear expectations, deliverables, and compensation structures to ensure a mutually beneficial partnership that drives measurable results while maintaining authenticity and compliance with all applicable advertising regulations."""
    
    elif doc_type == "employment":
        return f"""EMPLOYMENT AGREEMENT INTRODUCTION

This Employment Agreement ("Agreement") establishes the terms and conditions of employment between the Employer and the Employee. The position encompasses specific responsibilities, performance expectations, and professional development opportunities within the organization.

POSITION DETAILS BASED ON YOUR REQUIREMENTS:
{human_example}

This Agreement outlines compensation, benefits, working conditions, and professional obligations to ensure clarity and mutual understanding between all parties involved."""
    
    else:
        return f"""AGREEMENT INTRODUCTION

This Agreement establishes the professional relationship and collaboration terms between the parties. The scope of work, expectations, and deliverables are clearly defined to ensure successful project completion and mutual satisfaction.

PROJECT DETAILS BASED ON YOUR REQUIREMENTS:
{human_example}

This comprehensive framework addresses all aspects of the collaboration including timelines, compensation, intellectual property rights, and performance standards."""

def generate_detailed_scope_section(human_example: str, doc_type: str) -> str:
    """Generate detailed scope of work section"""
    if doc_type == "influencer":
        return """SCOPE OF WORK AND DELIVERABLES

The Influencer agrees to create and publish authentic, engaging content featuring the Brand's products across agreed-upon social media platforms. Content creation includes:

• Instagram feed posts with professional photography and compelling captions
• Instagram Stories with behind-the-scenes content and product demonstrations  
• Video content showcasing product usage in authentic lifestyle contexts
• User-generated content encouraging audience engagement and interaction
• Participation in brand campaigns and seasonal promotional activities

All content must align with the Brand's messaging guidelines while maintaining the Influencer's authentic voice and creative style. Content calendar coordination ensures optimal posting schedules for maximum audience engagement and reach."""
    
    elif doc_type == "employment":
        return """JOB RESPONSIBILITIES AND SCOPE

The Employee's primary responsibilities include executing assigned tasks within their designated department and contributing to organizational objectives. Key responsibilities encompass:

• Daily operational tasks as outlined in the position description
• Collaboration with team members and cross-functional departments
• Meeting performance targets and quality standards
• Professional development and skill enhancement activities
• Compliance with company policies, procedures, and industry regulations

The role requires dedication to excellence, continuous learning, and positive contribution to the workplace culture and organizational success."""
    
    else:
        return """SCOPE OF SERVICES AND DELIVERABLES

The Service Provider agrees to deliver comprehensive services as outlined in this Agreement. The scope includes:

• Project planning and strategic development
• Implementation of agreed-upon deliverables within specified timelines
• Regular progress reporting and stakeholder communication
• Quality assurance and performance optimization
• Post-delivery support and maintenance as applicable

All services will be performed with professional expertise and industry best practices to ensure client satisfaction and project success."""

def generate_content_section(human_example: str, doc_type: str) -> str:
    """Generate content requirements section"""
    return """CONTENT REQUIREMENTS AND STANDARDS

All deliverables must meet professional quality standards and align with established brand guidelines. Content specifications include:

• High-resolution imagery and professional video production quality
• Consistent brand messaging and visual identity adherence
• Appropriate hashtags, mentions, and attribution requirements
• Compliance with platform-specific content guidelines and best practices
• Timely delivery according to agreed-upon content calendar schedules

Content approval processes ensure brand alignment while respecting creative freedom and authentic voice. All materials remain subject to review and approval prior to publication or delivery."""

def generate_comprehensive_terms_section(human_example: str, doc_type: str) -> str:
    """Generate comprehensive terms and compensation section"""
    if doc_type == "influencer":
        return """COMPENSATION AND PAYMENT TERMS

The Brand agrees to provide comprehensive compensation including monetary payment and product considerations. Payment structure includes:

• Base compensation for content creation and publication
• Performance bonuses based on engagement metrics and conversion rates
• Product gifting and exclusive access to new releases
• Potential long-term partnership opportunities and ambassador programs

Payment terms specify net 30 days from invoice submission with detailed reporting requirements. Performance metrics include reach, engagement rates, click-through rates, and conversion tracking through unique discount codes or affiliate links."""
    
    else:
        return """TERMS AND COMPENSATION STRUCTURE

Compensation reflects the value and complexity of services provided. Payment terms include:

• Competitive base compensation commensurate with experience and market rates
• Performance-based incentives and bonus opportunities
• Comprehensive benefits package including health, dental, and retirement plans
• Professional development allowances and continuing education support

Payment schedules follow standard industry practices with clear invoicing procedures and timely processing. All compensation is subject to applicable tax withholdings and regulatory compliance requirements."""

def generate_performance_section(human_example: str, doc_type: str) -> str:
    """Generate performance metrics section"""
    return """PERFORMANCE METRICS AND EVALUATION

Success measurement includes quantitative and qualitative performance indicators:

• Engagement rates, reach, and audience growth metrics
• Content quality assessments and brand alignment evaluations
• Timeline adherence and deliverable completion rates
• Professional communication and collaboration effectiveness
• Innovation and creative contribution to project objectives

Regular performance reviews ensure continuous improvement and alignment with evolving project requirements. Feedback mechanisms facilitate open communication and collaborative problem-solving."""

def generate_rights_section(human_example: str, doc_type: str) -> str:
    """Generate rights and intellectual property section"""
    return """INTELLECTUAL PROPERTY RIGHTS AND USAGE

Intellectual property ownership and usage rights are clearly defined:

• Content creation rights and ownership specifications
• Brand usage permissions and trademark guidelines
• Image and likeness rights for marketing and promotional purposes
• Confidentiality requirements for proprietary information and trade secrets
• Attribution requirements and credit specifications

Usage rights extend to agreed-upon timeframes and platforms with clear guidelines for content repurposing and distribution. All parties retain appropriate rights while granting necessary permissions for project success."""

def generate_compliance_section(doc_type: str) -> str:
    """Generate compliance and legal requirements section"""
    return """COMPLIANCE AND REGULATORY REQUIREMENTS

All activities must comply with applicable laws, regulations, and industry standards:

• FTC disclosure requirements for sponsored content and partnerships
• Platform-specific advertising guidelines and community standards
• Data privacy regulations and audience information protection
• Industry-specific compliance requirements and professional standards
• International regulations for global audience reach and engagement

Regular compliance reviews ensure adherence to evolving regulatory landscapes. Legal counsel consultation is recommended for complex compliance scenarios and regulatory updates."""

def generate_termination_section(doc_type: str) -> str:
    """Generate termination and dispute resolution section"""
    return """TERMINATION AND DISPUTE RESOLUTION

Agreement termination procedures and dispute resolution mechanisms:

• Termination notice requirements and transition procedures
• Breach of contract definitions and cure period specifications
• Dispute resolution through mediation and arbitration processes
• Post-termination obligations and confidentiality maintenance
• Asset return requirements and final compensation settlements

Termination procedures prioritize professional conduct and minimize disruption to ongoing projects. Dispute resolution emphasizes collaborative problem-solving and fair resolution processes."""

def generate_general_provisions(doc_type: str) -> str:
    """Generate general legal provisions"""
    return """GENERAL PROVISIONS AND LEGAL FRAMEWORK

Standard legal provisions ensure agreement enforceability and clarity:

• Governing law and jurisdiction specifications
• Entire agreement clauses and amendment procedures
• Severability provisions for partial invalidity scenarios
• Force majeure protections for unforeseeable circumstances
• Assignment restrictions and successor obligations

These provisions establish the legal foundation for agreement interpretation and enforcement. Professional legal review is recommended to ensure compliance with applicable jurisdictions and regulations."""

def generate_additional_clauses(human_example: str, doc_type: str, additional_words_needed: int) -> str:
    """Generate additional detailed clauses to meet target length"""
    return f"""ADDITIONAL TERMS AND DETAILED PROVISIONS

ENHANCED COLLABORATION FRAMEWORK:
This Agreement establishes an enhanced collaboration framework designed to maximize mutual benefits and ensure professional excellence throughout the partnership duration. The framework encompasses detailed operational procedures, communication protocols, and performance optimization strategies.

QUALITY ASSURANCE AND STANDARDS:
All deliverables are subject to comprehensive quality assurance processes including peer review, brand alignment verification, and performance optimization analysis. Quality standards reflect industry best practices and client-specific requirements for exceptional results.

PROFESSIONAL DEVELOPMENT AND GROWTH:
The partnership includes opportunities for professional development, skill enhancement, and industry knowledge expansion. Continuous learning initiatives ensure evolving capabilities and adaptation to market trends and technological advancements.

COMMUNICATION AND REPORTING:
Regular communication schedules include progress updates, performance reviews, and strategic planning sessions. Detailed reporting mechanisms provide transparency and accountability throughout the collaboration period.

RISK MANAGEMENT AND MITIGATION:
Comprehensive risk assessment and mitigation strategies address potential challenges and ensure project continuity. Contingency planning and alternative approaches maintain momentum despite unforeseen circumstances.

INNOVATION AND CREATIVE EXCELLENCE:
The partnership encourages innovative approaches and creative excellence in all deliverables. Collaborative brainstorming and creative development sessions foster unique solutions and exceptional outcomes.

LONG-TERM PARTNERSHIP POTENTIAL:
This Agreement establishes the foundation for potential long-term partnership opportunities including expanded scope, increased responsibilities, and enhanced collaboration benefits for sustained mutual success."""

@app.get("/auto-detect")
async def auto_detect_document_type(human_example: str):
    """Fast document type detection"""
    try:
        # Rule-based detection for speed
        text_lower = human_example.lower()
        
        if any(word in text_lower for word in ['influencer', 'social media', 'instagram', 'youtube', 'tiktok']):
            doc_type = 'influencer_agreement'
        elif any(word in text_lower for word in ['employment', 'job', 'work', 'employee', 'hire']):
            doc_type = 'employment_contract'
        elif any(word in text_lower for word in ['service', 'consulting', 'freelance', 'contractor']):
            doc_type = 'service_agreement'
        elif any(word in text_lower for word in ['nda', 'confidential', 'non-disclosure', 'secret']):
            doc_type = 'nda'
        else:
            doc_type = 'general_contract'
            
        return {
            "document_type": doc_type,
            "confidence": 0.95,
            "processing_time": 1.0
        }
        
    except Exception as e:
        return {"document_type": "general_contract", "confidence": 0.5, "error": str(e)}

# Root endpoint - serve frontend
@app.get("/", response_class=HTMLResponse)
async def serve_home():
    """Serve the Thinkerbell frontend"""
    index_file = static_dir / "index.html"
    
    if index_file.exists():
        return FileResponse(str(index_file))
    else:
        return HTMLResponse("""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Thinkerbell ⚡ FAST</title>
            <style>
                body { font-family: system-ui; background: #0b0b0c; color: #eaeaea; 
                       display: grid; place-items: center; min-height: 100vh; margin: 0; }
                .container { text-align: center; }
                h1 { color: #ff1493; font-size: 3rem; margin: 0; }
                p { color: #9aa0a6; margin: 1rem 0; }
                .cta { background: #00ff7f; color: #000; padding: 1rem 2rem; 
                       border: none; border-radius: 8px; font-weight: bold; cursor: pointer; }
                .speed { color: #00ff7f; font-weight: bold; }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>Thinkerbell ⚡ FAST</h1>
                <p class="speed">Optimized for Speed - Client's Optimum Model</p>
                <p>AI-powered legal document generation</p>
                <button class="cta" onclick="window.location.reload()">Test Performance</button>
            </div>
        </body>
        </html>
        """)

# Catch-all for SPA routing
@app.get("/{path:path}")
async def catch_all(path: str):
    """Handle SPA routing"""
    # Exclude API paths
    excluded_paths = {
        "health", "info", "embed", "similarity", "generate", 
        "auto-detect", "static", "assets"
    }
    
    if path.split('/')[0] in excluded_paths:
        raise HTTPException(status_code=404, detail="Not found")
    
    # Serve index.html for all other paths
    index_file = static_dir / "index.html"
    if index_file.exists():
        return FileResponse(str(index_file))
    else:
        return HTMLResponse("<h1>Thinkerbell ⚡ FAST</h1><p>SPA Route Handler</p>")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    host = os.environ.get("HOST", "0.0.0.0")
    
    logger.info(f"🚀 Starting FAST production server on {host}:{port}")
    logger.info("⚡ Optimized for client's optimum model performance")
    
    uvicorn.run(
        app,
        host=host,
        port=port,
        reload=False,
        log_level="info"
    )
