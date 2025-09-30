"""
Request models for API endpoints
"""

from typing import List, Optional
from pydantic import BaseModel

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

class AnalyzeRequest(BaseModel):
    content: str
    analyze_type: str = "general"

class GenerateRequest(BaseModel):
    human_example: str
    target_length: int = 500
    style_preference: str = "professional"
    document_type: str = "agreement"

class BatchGenerateRequest(BaseModel):
    requests: List[GenerateRequest]
    batch_name: str = "batch_job"
