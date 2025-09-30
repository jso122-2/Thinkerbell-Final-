"""
Model service for ML operations
"""

import os
import logging
from typing import List, Dict, Any, Optional
from pathlib import Path

from fastapi import HTTPException

from ..core.config import settings
from ..core.dependencies import HAS_ML_DEPS, HAS_NUMPY, np

logger = logging.getLogger(__name__)

class ModelService:
    """Service class for model operations"""
    
    def __init__(self):
        self.model = None
        self.model_path = settings.MODEL_DIR
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
        
        # Import here to avoid issues when ML deps not available
        from sentence_transformers import SentenceTransformer
        
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
            logger.info(f"Loading fallback model: {settings.FALLBACK_MODEL}")
            self.model = SentenceTransformer(settings.FALLBACK_MODEL)
            logger.info(f"Fallback model loaded successfully! Dimension: {self.model.get_sentence_embedding_dimension()}")
            return True
        except Exception as e:
            logger.error(f"Failed to load fallback model: {e}")
            return False
    
    def encode_texts(self, texts: List[str], normalize: bool = True):
        """Encode texts to embeddings"""
        if not HAS_ML_DEPS:
            raise HTTPException(status_code=503, detail="ML dependencies not available")
        if not self.model:
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

# Global model service instance
model_service = ModelService()
