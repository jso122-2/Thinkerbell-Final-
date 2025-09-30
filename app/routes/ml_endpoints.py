"""
Machine Learning API endpoints
"""

import time
from typing import List
from fastapi import APIRouter, HTTPException

from ..services.model_service import model_service
from ..models import (
    EmbedRequest, SimilarityRequest, SearchRequest, 
    AnalyzeRequest, GenerateRequest,
    EmbedResponse, SimilarityResponse, SearchResponse,
    AnalyzeResponse, GenerateResponse
)

router = APIRouter()

@router.post("/embed", response_model=EmbedResponse)
async def embed_texts(request: EmbedRequest):
    """Generate embeddings for input texts"""
    start_time = time.time()
    
    # Initialize model if needed
    if not model_service.initialize():
        raise HTTPException(status_code=503, detail="Model service unavailable")
    
    embeddings = model_service.encode_texts(request.texts, request.normalize)
    
    return EmbedResponse(
        embeddings=embeddings.tolist(),
        processing_time=time.time() - start_time,
        texts_count=len(request.texts)
    )

@router.post("/similarity", response_model=SimilarityResponse)
async def compute_similarity(request: SimilarityRequest):
    """Compute semantic similarity between two texts"""
    start_time = time.time()
    
    # Initialize model if needed
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

@router.post("/search", response_model=SearchResponse)
async def search_documents(request: SearchRequest):
    """Search for similar documents"""
    start_time = time.time()
    
    # Initialize model if needed
    if not model_service.initialize():
        raise HTTPException(status_code=503, detail="Model service unavailable")
    
    results = model_service.search_similar(
        request.query, 
        request.documents, 
        request.top_k
    )
    
    return SearchResponse(
        results=results,
        query=request.query,
        processing_time=time.time() - start_time
    )

@router.post("/analyze", response_model=AnalyzeResponse)
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

@router.post("/generate", response_model=GenerateResponse)
async def generate_content(request: GenerateRequest):
    """Generate legal content based on example"""
    start_time = time.time()
    
    # Initialize model if needed
    if not model_service.initialize():
        raise HTTPException(status_code=503, detail="Model service unavailable")
    
    # For now, return a placeholder response
    # This would integrate with your content generation logic
    generated_text = f"Generated {request.document_type} content based on the provided example. " \
                    f"Style: {request.style_preference}. Target length: {request.target_length} characters."
    
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

@router.get("/model/info")
async def get_model_info():
    """Get information about the loaded model"""
    return model_service.get_model_info()
