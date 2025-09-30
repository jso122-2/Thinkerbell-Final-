"""
Response models for API endpoints
"""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel

class HealthResponse(BaseModel):
    status: str
    model_loaded: bool
    model_path: str
    model_dimension: Optional[int] = None
    uptime_seconds: float

class EmbedResponse(BaseModel):
    embeddings: List[List[float]]
    processing_time: float
    texts_count: int

class SimilarityResponse(BaseModel):
    similarity: float
    interpretation: str
    processing_time: float

class SearchResult(BaseModel):
    document_index: int
    document: str
    similarity: float
    preview: str

class SearchResponse(BaseModel):
    results: List[SearchResult]
    query: str
    processing_time: float

class AnalyzeResponse(BaseModel):
    analysis: Dict[str, Any]
    processing_time: float

class GenerateResponse(BaseModel):
    generated_text: str
    similarity_to_example: float
    word_count: int
    processing_time: float
    generation_metadata: Dict[str, Any]

class BatchResponse(BaseModel):
    batch_id: str
    status: str
    created_at: str
    total_requests: int
