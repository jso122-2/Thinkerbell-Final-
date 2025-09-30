#!/usr/bin/env python3
"""
Enhanced Thinkerbell Backend API Server
Serves the newly trained model with comprehensive endpoints
Full-stack deployment with React frontend integration
"""

import os
import json
import time
import logging
import re
from typing import List, Dict, Any, Optional
from pathlib import Path
import zipfile
import io
from datetime import datetime

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
import uvicorn

# Try to import numpy (optional for basic server functionality)
try:
    import numpy as np
    HAS_NUMPY = True
except ImportError:
    HAS_NUMPY = False
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
except ImportError as e:
    logger.error(f"ML dependencies not available: {e}")
    HAS_ML_DEPS = False

# Configuration
MODEL_DIR = os.environ.get(
    "THINKERBELL_MODEL_DIR", 
    "models/thinkerbell-encoder-best"
)
PORT = int(os.environ.get("PORT", 8000))
HOST = os.environ.get("HOST", "0.0.0.0")
ENV = os.environ.get("THINKERBELL_ENV", "development")

# Production model fallback
FALLBACK_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

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

class AnalyzeRequest(BaseModel):
    content: str
    analyze_type: str = "influencer_agreement"

class GenerateRequest(BaseModel):
    human_example: str
    target_length: int = 700
    style_preference: str = "professional"
    document_type: str = "legal_template"

class BatchGenerateRequest(BaseModel):
    batch_inputs: List[Dict[str, Any]]  # List of GenerateRequest-like objects
    batch_name: str = "Batch Processing"
    
class BatchProcessingStatus(BaseModel):
    batch_id: str
    status: str  # "processing", "completed", "failed"
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

class EmbedResponse(BaseModel):
    embeddings: List[List[float]]
    processing_time: float
    texts_count: int

class SimilarityResponse(BaseModel):
    similarity: float
    interpretation: str
    processing_time: float

class SearchResponse(BaseModel):
    results: List[Dict[str, Any]]
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

class AutoDetectRequest(BaseModel):
    text: str

class AutoDetectResponse(BaseModel):
    target_length: int
    style_preference: str
    document_type: str
    confidence_scores: Dict[str, float]
    reasoning: Dict[str, str]

# Global variables
app = FastAPI(
    title="Thinkerbell Enhanced API",
    description="API for the newly trained Thinkerbell model with comprehensive endpoints",
    version="2.0.0"
)
model = None
start_time = time.time()

# Batch processing storage (in production, use Redis or database)
batch_jobs = {}
import uuid
from datetime import datetime

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve static frontend files
static_dir = Path("static")
if static_dir.exists():
    app.mount("/static", StaticFiles(directory="static"), name="static")

class ModelService:
    """Service class for model operations"""
    
    def __init__(self):
        self.model = None
        self.model_path = MODEL_DIR
        self.load_model()
    
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
    
    def analyze_content(self, content: str, analyze_type: str = "influencer_agreement") -> Dict[str, Any]:
        """Analyze content for specific patterns"""
        # Basic analysis - can be extended based on needs
        analysis = {
            "content_length": len(content),
            "word_count": len(content.split()),
            "sentence_count": len([s for s in content.split('.') if s.strip()]),
            "analyze_type": analyze_type,
            "embedding_stats": {}
        }
        
        # Get embedding statistics
        try:
            if HAS_ML_DEPS and HAS_NUMPY:
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
        
        # Content-specific analysis
        if analyze_type == "influencer_agreement":
            analysis["agreement_features"] = self._analyze_influencer_agreement(content)
        
        return analysis
    
    def _analyze_influencer_agreement(self, content: str) -> Dict[str, Any]:
        """Analyze influencer agreement specific features"""
        content_lower = content.lower()
        
        # Key terms detection
        brand_terms = ["brand", "company", "partnership", "collaboration", "sponsor"]
        content_terms = ["content", "post", "story", "video", "photo", "reel"]
        legal_terms = ["agreement", "contract", "terms", "conditions", "rights", "usage"]
        timeline_terms = ["days", "weeks", "months", "deadline", "duration", "period"]
        
        features = {
            "has_brand_terms": any(term in content_lower for term in brand_terms),
            "has_content_terms": any(term in content_lower for term in content_terms),
            "has_legal_terms": any(term in content_lower for term in legal_terms),
            "has_timeline_terms": any(term in content_lower for term in timeline_terms),
            "brand_term_count": sum(1 for term in brand_terms if term in content_lower),
            "content_term_count": sum(1 for term in content_terms if term in content_lower),
            "legal_term_count": sum(1 for term in legal_terms if term in content_lower),
            "timeline_term_count": sum(1 for term in timeline_terms if term in content_lower)
        }
        
        # Overall agreement score
        total_terms = sum([
            features["brand_term_count"],
            features["content_term_count"], 
            features["legal_term_count"],
            features["timeline_term_count"]
        ])
        
        features["agreement_score"] = min(total_terms / 10.0, 1.0)  # Normalize to 0-1
        
        return features
    
    def generate_similar_text(self, human_example: str, target_length: int = 700, 
                             style_preference: str = "professional", 
                             document_type: str = "legal_template") -> Dict[str, Any]:
        """Generate similar legal text based on human example"""
        
        # Load sample legal templates from our dataset for reference
        sample_templates = self._load_sample_templates()
        
        # Find most similar templates to the human example
        similar_templates = self.search_similar(human_example, sample_templates, top_k=3)
        
        # Generate new text by combining patterns from similar templates
        generated_text = self._generate_from_templates(
            human_example, similar_templates, target_length, style_preference
        )
        
        # Calculate similarity to original example
        similarity = self.compute_similarity(human_example, generated_text)
        
        return {
            "generated_text": generated_text,
            "similarity_to_example": similarity,
            "word_count": len(generated_text.split()),
            "generation_metadata": {
                "style_preference": style_preference,
                "document_type": document_type,
                "reference_templates_used": len(similar_templates),
                "target_length": target_length,
                "actual_length": len(generated_text)
            }
        }
    
    def _load_sample_templates(self) -> List[str]:
        """Load sample legal templates from dataset"""
        try:
            # Try to load from the debugged dataset
            dataset_path = Path("/home/black-cat/Documents/Thinkerbell/debugged_dataset.json")
            if dataset_path.exists():
                with open(dataset_path, 'r') as f:
                    data = json.load(f)
                
                templates = []
                if isinstance(data, dict) and 'dataset' in data:
                    samples = data['dataset']
                elif isinstance(data, list):
                    samples = data
                else:
                    samples = [data]
                
                for sample in samples[:50]:  # Use first 50 as templates
                    if 'content' in sample:
                        templates.append(sample['content'])
                    elif 'text' in sample:
                        templates.append(sample['text'])
                
                if templates:
                    return templates
        except Exception as e:
            logger.warning(f"Could not load dataset templates: {e}")
        
        # Fallback to hardcoded templates
        return [
            "INFLUENCER MARKETING AGREEMENT\n\nThis agreement between [Brand Name] and [Influencer Name] establishes the terms for social media collaboration. The influencer agrees to create authentic content featuring brand products across specified platforms including Instagram, TikTok, and YouTube. Content requirements include product mentions, brand hashtags, and usage of provided creative assets. The collaboration period spans 60 days with exclusive content rights during this timeframe. Compensation includes monetary payment of $[Amount] plus product gifting valued at $[Value]. Performance metrics will be tracked including engagement rates, reach, impressions, and conversion through unique discount codes. The influencer maintains creative control while adhering to brand guidelines and FTC disclosure requirements.",
            
            "BRAND PARTNERSHIP CONTRACT\n\nThis contract governs the partnership between [Company] and [Content Creator] for promotional activities. The creator commits to producing high-quality content that aligns with brand values and messaging. Deliverables include [Number] Instagram posts, [Number] Stories, and [Number] video content pieces. All content must be approved by brand representatives before publication. Usage rights are granted for 12 months with options for renewal. Payment terms include 50% upfront and 50% upon completion of deliverables. The creator agrees to maintain professional standards and avoid conflicting brand partnerships during the contract period.",
            
            "SOCIAL MEDIA COLLABORATION AGREEMENT\n\nThis agreement outlines the terms of collaboration between [Brand] and [Influencer] for digital marketing campaigns. The influencer will create engaging content showcasing brand products in authentic lifestyle contexts. Content must include proper attribution, brand mentions, and compliance with advertising standards. The campaign duration is 90 days with performance benchmarks for engagement and reach. Compensation structure includes base fee plus performance bonuses based on achieved metrics. Both parties agree to maintain confidentiality regarding campaign details and performance data.",
            
            "CONTENT CREATION PARTNERSHIP\n\nThis partnership agreement establishes terms for ongoing content collaboration between [Brand] and [Creator]. The creator will develop original content featuring brand products with creative freedom within brand guidelines. Content calendar includes weekly posts across multiple platforms with seasonal campaign participation. Rights and usage permissions extend to brand's marketing materials and advertising campaigns. Performance tracking includes detailed analytics reporting and ROI measurement. The partnership includes product seeding, event invitations, and potential long-term ambassador opportunities."
        ]
    
    def _generate_from_templates(self, human_example: str, similar_templates: List[Dict], 
                                target_length: int, style_preference: str) -> str:
        """Generate comprehensive legal text based on human example and target length"""
        
        # Extract key elements from human example
        example_words = human_example.lower().split()
        
        # Determine document type and header
        if any(term in example_words for term in ["influencer", "social", "media"]):
            header = "INFLUENCER MARKETING AGREEMENT"
            doc_type = "influencer"
        elif any(term in example_words for term in ["brand", "partnership"]):
            header = "BRAND PARTNERSHIP CONTRACT"
            doc_type = "partnership"
        elif any(term in example_words for term in ["content", "creation"]):
            header = "CONTENT CREATION AGREEMENT"
            doc_type = "content"
        else:
            header = "COLLABORATION AGREEMENT"
            doc_type = "general"
        
        # Build comprehensive legal document with multiple sections
        sections = []
        
        # 1. Header and Introduction (target: ~50-80 words)
        sections.append(f"{header}\n\n")
        intro_section = self._generate_detailed_introduction(human_example, doc_type, style_preference)
        sections.append(intro_section)
        
        # 2. Scope of Work/Services (target: ~100-150 words)
        scope_section = self._generate_detailed_scope_section(human_example, doc_type)
        sections.append(scope_section)
        
        # 3. Content Requirements and Deliverables (target: ~150-200 words)
        content_section = self._generate_content_section(human_example, similar_templates)
        sections.append(content_section)
        
        # 4. Terms and Compensation (target: ~200-300 words)
        terms_section = self._generate_comprehensive_terms_section(human_example, doc_type)
        sections.append(terms_section)
        
        # 5. Performance Metrics and Standards (target: ~100-150 words)
        performance_section = self._generate_performance_section(human_example)
        sections.append(performance_section)
        
        # 6. Rights and Intellectual Property (target: ~150-200 words)
        rights_section = self._generate_rights_section(human_example, doc_type)
        sections.append(rights_section)
        
        # 7. Compliance and Legal Requirements (target: ~100-150 words)
        compliance_section = self._generate_compliance_section(doc_type)
        sections.append(compliance_section)
        
        # 8. Termination and Dispute Resolution (target: ~100-150 words)
        termination_section = self._generate_termination_section(doc_type)
        sections.append(termination_section)
        
        # Join all sections
        generated_text = "\n\n".join(sections)
        
        # Adjust to target length by expanding or condensing content
        current_words = len(generated_text.split())
        
        if current_words < target_length * 0.8:
            # Add more detailed clauses to reach target length
            additional_sections = self._generate_additional_clauses(human_example, doc_type, target_length - current_words)
            generated_text += "\n\n" + additional_sections
        elif current_words > target_length * 1.3:
            # Condense content while maintaining legal completeness
            words = generated_text.split()
            # Keep essential legal structure but trim to reasonable length
            target_words = min(target_length, len(words))
            generated_text = " ".join(words[:target_words])
            if target_words < len(words):
                generated_text += "..."
        
        return generated_text
    
    def _extract_key_information(self, human_example: str) -> Dict[str, str]:
        """Extract key information from human example automatically with comprehensive threading"""
        import re
        
        # Initialize with enhanced field structure for better threading
        extracted_info = {
            'brand_name': '[BRAND NAME]',
            'client_name': '[CLIENT NAME]',
            'partner_name': '[PARTNER NAME]',
            'influencer_name': '[INFLUENCER NAME]',
            'creator_name': '[CREATOR NAME]',
            'company_name': '[COMPANY NAME]',
            'state': '[STATE]',
            'country': '[COUNTRY]',
            'city': '[CITY]',
            'duration': '[DURATION]',
            'compensation': '[COMPENSATION]',
            'platforms': '[PLATFORMS]',
            'deliverables': '[DELIVERABLES]',
            'contact_person': '[CONTACT PERSON]',
            'email': '[EMAIL]',
            'phone': '[PHONE]',
            'address': '[ADDRESS]',
            'abn': '[ABN]',
            'acn': '[ACN]'
        }
        
        # Enhanced entity threading system
        self.entity_threads = {
            'companies': [],
            'individuals': [],
            'locations': [],
            'contacts': [],
            'legal_entities': []
        }
        
        text = human_example
        
        # First pass: Extract all potential entities and build threading context
        self._extract_all_entities(text, extracted_info)
        
        # Second pass: Apply threading logic to ensure consistency
        self._apply_entity_threading(extracted_info)
        
        # Third pass: Validate and cross-reference entities
        self._validate_entity_consistency(extracted_info)
        
        return extracted_info
    
    def _extract_all_entities(self, text: str, extracted_info: Dict[str, str]) -> None:
        """Extract all entities with comprehensive pattern matching"""
        import re
        
        # Extract Australian Business Numbers (ABN) and Australian Company Numbers (ACN)
        abn_pattern = r'ABN\s+(\d{2}\s+\d{3}\s+\d{3}\s+\d{3}|\d{11})'
        acn_pattern = r'ACN\s+(\d{3}\s+\d{3}\s+\d{3}|\d{9})'
        
        abn_matches = re.findall(abn_pattern, text, re.IGNORECASE)
        if abn_matches:
            extracted_info['abn'] = abn_matches[0].replace(' ', ' ')  # Normalize spacing
            
        acn_matches = re.findall(acn_pattern, text, re.IGNORECASE)
        if acn_matches:
            extracted_info['acn'] = acn_matches[0].replace(' ', ' ')  # Normalize spacing
        
        # Extract comprehensive location information (Australian focus)
        self._extract_location_information(text, extracted_info)
        
        # Extract contact information
        self._extract_contact_information(text, extracted_info)
        
        # Extract addresses
        self._extract_address_information(text, extracted_info)
        
        # Extract brand/company names - comprehensive patterns for all scenarios
        brand_patterns = [
            # Pattern 1: "CompanyName needs/wants/requires/is looking for" (start of sentence)
            r'(?:^|\. )([A-Z][a-zA-Z\s&\.]{2,35}?)\s+(?:needs|wants|requires|is\s+looking\s+for)',
            
            # Pattern 2: Company suffixes - "CompanyName Solutions/Technologies/Corp/Inc/etc"
            r'([A-Z][a-zA-Z\s&\.]{1,30}?)\s+(?:Solutions|Technologies|Systems|Innovations|Corp|Corporation|Inc|Incorporated|LLC|Ltd|Limited|Company|Co|Group|Enterprises|Studios|Motors|Academy|Platform|Boutique|Nutrition)',
            
            # Pattern 3: "promoting our CompanyName" or "for our CompanyName"
            r'(?:promoting|for)\s+(?:our\s+)?([A-Z][a-zA-Z\s&\.]{2,30}?)\s+(?:product|service|app|software|platform|brand|line|collection|ecosystem)',
            
            # Pattern 4: "work with CompanyName" or "partner with CompanyName"
            r'(?:work\s+with|partner\s+with|collaborate\s+with|agreement\s+with)\s+([A-Z][a-zA-Z\s&\.]{2,30}?)(?:\s+(?:for|to|on|needs|wants))',
            
            # Pattern 5: "CompanyName's product/service" (possessive)
            r"([A-Z][a-zA-Z\s&\.]{2,30}?)'s\s+(?:product|service|app|software|platform|line|collection|ecosystem)",
            
            # Pattern 6: "We will pay" - look for company before this
            r'([A-Z][a-zA-Z\s&\.]{2,30}?)\s+(?:will\s+pay|offers|provides|pays)',
            
            # Pattern 7: Simple start pattern - "CompanyName [verb]" 
            r'(?:^|\. )([A-Z][a-zA-Z\s&\.]{2,35}?)\s+(?:requires|wants|is|has|offers|provides)',
            
            # Pattern 8: "between CompanyName and" or "with CompanyName for"
            r'(?:between|with)\s+([A-Z][a-zA-Z\s&\.]{2,30}?)\s+(?:and|for|to)',
            
            # Pattern 9: Tag mentions - "@CompanyName" 
            r'@([A-Z][a-zA-Z\s&\.]{2,30}?)(?:\s|,|\.)',
            
            # Pattern 10: Very broad start-of-text pattern for any company name
            r'^([A-Z][a-zA-Z\s&\.]{3,35}?)(?:\s+(?:needs|wants|requires|is|has|offers|provides|will))',
            
            # Pattern 11: CLIENT/BRAND patterns
            r'(?:CLIENT|BRAND)\s+([A-Z][a-zA-Z\s&\.]{2,40}?)(?:\s+(?:Pty|Ltd|Inc|Corp|Company|Australia))',
            
            # Pattern 12: "CompanyName Pty Ltd" - direct company suffix patterns
            r'([A-Z][a-zA-Z\s&\.]{2,30}?)\s+(?:Pty\s+Ltd|Ltd|Inc|Corp|Company|Corporation|LLC)',
            
            # Pattern 13: "BETWEEN CompanyName" - legal document patterns
            r'(?:BETWEEN|between)\s+([A-Z][a-zA-Z\s&\.]{2,30}?)\s+(?:Pty|Ltd|Inc|Corp|Company|\()',
            
            # Pattern 14: Extract full company name with suffix
            r'([A-Z][a-zA-Z\s&\.]{2,30}?\s+(?:Pty\s+Ltd|Australia\s+Pty\s+Ltd|Ltd|Inc|Corp|Company|Corporation|LLC))',
        ]
        
        for pattern in brand_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                for match in matches:
                    brand_name = match.strip()
                    # Clean up the match - remove extra spaces and fix capitalization
                    brand_name = ' '.join(word.capitalize() for word in brand_name.split())
                    
                    # More lenient validation - focus on excluding obvious non-company words
                    excluded_words = {
                        'we', 'they', 'our', 'the', 'this', 'that', 'their', 'some', 'any', 'all', 
                        'content', 'creator', 'influencer', 'with', 'for', 'and', 'or', 'will', 
                        'must', 'should', 'needs', 'wants', 'has', 'is', 'are', 'was', 'were',
                        'marketing', 'agreement', 'contract', 'partnership', 'collaboration'
                    }
                    
                    if (len(brand_name) >= 3 and len(brand_name) <= 40 and
                        brand_name[0].isupper() and
                        brand_name.lower() not in excluded_words and
                        not any(brand_name.lower().startswith(word + ' ') for word in excluded_words) and
                        not any(brand_name.lower().endswith(' ' + word) for word in excluded_words) and
                        # Must contain at least one letter (not just numbers/symbols)
                        any(c.isalpha() for c in brand_name)):
                        
                        extracted_info['brand_name'] = brand_name
                        extracted_info['company_name'] = brand_name
                        extracted_info['client_name'] = brand_name
                        break
                if extracted_info['brand_name'] != '[BRAND NAME]':
                    break
        
        # Extract influencer/creator names - more precise patterns
        influencer_patterns = [
            # Pattern: "influencer/creator Name"
            r'(?:influencer|creator|blogger|youtuber|tiktoker|content\s+creator)\s+([A-Z][a-zA-Z]{2,15}(?:\s+[A-Z][a-zA-Z]{2,25})*)',
            # Pattern: "with Name for/to"
            r'(?:with|for)\s+([A-Z][a-zA-Z]{2,15}(?:\s+[A-Z][a-zA-Z]{2,25})*)\s+(?:for|to|will|creating|on)',
            # Pattern: "Name will create/make/produce"
            r'([A-Z][a-zA-Z]{2,15}(?:\s+[A-Z][a-zA-Z]{2,25})*)\s+(?:will|must|should)\s+(?:create|make|produce|post|showcase)',
            # Pattern: "agreement with Name"
            r'(?:agreement|partnership|contract)\s+with\s+([A-Z][a-zA-Z]{2,15}(?:\s+[A-Z][a-zA-Z]{2,25})*)',
            # Pattern: "pay Name $amount"
            r'(?:pay|paying)\s+([A-Z][a-zA-Z]{2,15}(?:\s+[A-Z][a-zA-Z]{2,25})*)\s+\$',
        ]
        
        for pattern in influencer_patterns:
            matches = re.findall(pattern, text)
            if matches:
                for match in matches:
                    name = match.strip()
                    name_parts = name.split()
                    # Validate: 1-3 words, proper capitalization, not common words
                    if (len(name_parts) <= 3 and len(name) >= 3 and len(name) <= 40 and
                        all(part[0].isupper() and len(part) >= 2 for part in name_parts) and
                        name.lower() not in ['they', 'them', 'the', 'our', 'will', 'must', 'should', 'needs', 'content creator', 'social media'] and
                        not any(word in name.lower() for word in ['company', 'corp', 'inc', 'llc', 'solutions', 'technologies'])):
                        extracted_info['influencer_name'] = name
                        extracted_info['creator_name'] = name
                        extracted_info['partner_name'] = name
                        break
                if extracted_info['influencer_name'] != '[INFLUENCER NAME]':
                    break
        
        # Extract duration/timeline - more comprehensive
        duration_patterns = [
            # Pattern: "X months/weeks/days"
            r'(\d+\s+(?:day|week|month|year)s?)',
            # Pattern: "over/for/during X months"
            r'(?:over|for|during|spanning)\s+(\d+\s+(?:day|week|month|year)s?)',
            # Pattern: "X-month period/campaign/contract"
            r'(\d+)[-\s](?:day|week|month|year)\s+(?:period|campaign|contract|agreement|collaboration)',
            # Pattern: "X months starting"
            r'(\d+\s+(?:day|week|month|year)s?)\s+(?:starting|beginning)',
        ]
        
        for pattern in duration_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                duration = matches[0].strip()
                # Validate it's a reasonable duration
                if any(word in duration.lower() for word in ['day', 'week', 'month', 'year']):
                    extracted_info['duration'] = duration
                    break
        
        # Extract compensation - more precise monetary patterns
        compensation_patterns = [
            # Pattern: "$X,XXX monthly/per month"
            r'(\$[\d,]+(?:\.\d{2})?)\s+(?:monthly|per\s+month|each\s+month)',
            # Pattern: "pay $X,XXX"
            r'(?:pay|paying|compensation|salary)\s+(\$[\d,]+(?:\.\d{2})?)',
            # Pattern: "$X,XXX plus/and"
            r'(\$[\d,]+(?:\.\d{2})?)\s+(?:plus|and|\+)',
            # Pattern: standalone dollar amounts
            r'(\$[\d,]+(?:\.\d{2})?)',
        ]
        
        for pattern in compensation_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                comp = matches[0].strip()
                # Validate it's a reasonable amount (not too small/large)
                amount_str = comp.replace('$', '').replace(',', '')
                try:
                    amount = float(amount_str)
                    if 100 <= amount <= 1000000:  # Reasonable range
                        extracted_info['compensation'] = comp
                        break
                except ValueError:
                    continue
        
        # Extract platforms - case insensitive, comprehensive
        platform_keywords = ['instagram', 'tiktok', 'youtube', 'facebook', 'twitter', 'linkedin', 'snapchat', 'pinterest', 'twitch']
        found_platforms = []
        text_lower = text.lower()
        
        for platform in platform_keywords:
            if platform in text_lower:
                # Capitalize properly
                if platform == 'tiktok':
                    found_platforms.append('TikTok')
                elif platform == 'youtube':
                    found_platforms.append('YouTube')
                elif platform == 'linkedin':
                    found_platforms.append('LinkedIn')
                else:
                    found_platforms.append(platform.capitalize())
        
        if found_platforms:
            extracted_info['platforms'] = ', '.join(found_platforms)
        
        # Extract deliverables - more specific patterns
        deliverable_patterns = [
            # Pattern: "X Instagram posts, Y videos"
            r'(\d+\s+[A-Za-z]+\s+(?:post|video|story|reel|article|blog|review)s?)',
            # Pattern: "create X posts"
            r'(?:create|make|produce|deliver|publish)\s+(\d+\s+(?:post|video|story|reel|article|blog|review)s?)',
            # Pattern: "X posts and Y videos"
            r'(\d+\s+(?:post|video|story|reel|article|blog|review)s?)(?:\s+(?:and|,|\+)\s+\d+\s+(?:post|video|story|reel|article|blog|review)s?)*',
        ]
        
        deliverables = []
        for pattern in deliverable_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                if match not in deliverables:
                    deliverables.append(match)
        
        if deliverables:
            extracted_info['deliverables'] = ', '.join(deliverables[:5])  # Limit to first 5
        
        return extracted_info
    
    def _extract_location_information(self, text: str, extracted_info: Dict[str, str]) -> None:
        """Extract comprehensive location information with Australian focus"""
        import re
        
        # Australian states and territories
        australian_states = {
            'NSW': 'New South Wales', 'VIC': 'Victoria', 'QLD': 'Queensland', 
            'WA': 'Western Australia', 'SA': 'South Australia', 'TAS': 'Tasmania',
            'ACT': 'Australian Capital Territory', 'NT': 'Northern Territory',
            'New South Wales': 'NSW', 'Victoria': 'VIC', 'Queensland': 'QLD',
            'Western Australia': 'WA', 'South Australia': 'SA', 'Tasmania': 'TAS',
            'Australian Capital Territory': 'ACT', 'Northern Territory': 'NT'
        }
        
        # Extract Australian states/territories
        state_patterns = [
            # Pattern: "City, STATE postcode" or "City STATE postcode"
            r'([A-Z][a-zA-Z\s]+),?\s+(NSW|VIC|QLD|WA|SA|TAS|ACT|NT)\s+\d{4}',
            # Pattern: "of State" or "in State"
            r'(?:of|in)\s+(NSW|VIC|QLD|WA|SA|TAS|ACT|NT|New South Wales|Victoria|Queensland|Western Australia|South Australia|Tasmania|Australian Capital Territory|Northern Territory)',
            # Pattern: Full state names
            r'(New South Wales|Victoria|Queensland|Western Australia|South Australia|Tasmania|Australian Capital Territory|Northern Territory)',
        ]
        
        for pattern in state_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                for match in matches:
                    if isinstance(match, tuple):
                        # Extract state from tuple (city, state pattern)
                        state = match[1] if len(match) > 1 else match[0]
                    else:
                        state = match
                    
                    # Normalize state name
                    state_upper = state.upper()
                    if state_upper in australian_states:
                        extracted_info['state'] = state_upper
                        self.entity_threads['locations'].append({
                            'type': 'state',
                            'value': state_upper,
                            'full_name': australian_states.get(state_upper, state_upper)
                        })
                        break
                if extracted_info['state'] != '[STATE]':
                    break
        
        # Extract cities (Australian major cities)
        australian_cities = [
            'Sydney', 'Melbourne', 'Brisbane', 'Perth', 'Adelaide', 'Canberra', 
            'Darwin', 'Hobart', 'Gold Coast', 'Newcastle', 'Wollongong', 'Geelong',
            'Townsville', 'Cairns', 'Toowoomba', 'Ballarat', 'Bendigo', 'Albury',
            'Launceston', 'Mackay', 'Rockhampton', 'Bunbury', 'Bundaberg', 'Wagga Wagga',
            'Redfern', 'South Yarra', 'Surry Hills', 'Paddington', 'Newtown'
        ]
        
        city_patterns = [
            # Pattern: "City, STATE" or "of City"
            r'(?:of|in|at)\s+([A-Z][a-zA-Z\s]+?)(?:,|\s+(?:NSW|VIC|QLD|WA|SA|TAS|ACT|NT))',
            # Pattern: Direct city mentions
            r'\b(' + '|'.join(australian_cities) + r')\b',
        ]
        
        for pattern in city_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                for match in matches:
                    city = match.strip()
                    if city.title() in australian_cities:
                        extracted_info['city'] = city.title()
                        self.entity_threads['locations'].append({
                            'type': 'city',
                            'value': city.title()
                        })
                        break
                if extracted_info['city'] != '[CITY]':
                    break
        
        # Set country to Australia if Australian locations detected
        if (extracted_info['state'] != '[STATE]' or extracted_info['city'] != '[CITY]'):
            extracted_info['country'] = 'Australia'
            self.entity_threads['locations'].append({
                'type': 'country',
                'value': 'Australia'
            })
    
    def _extract_contact_information(self, text: str, extracted_info: Dict[str, str]) -> None:
        """Extract contact information including emails and phone numbers"""
        import re
        
        # Extract email addresses
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        emails = re.findall(email_pattern, text)
        if emails:
            extracted_info['email'] = emails[0]  # Take first email found
            self.entity_threads['contacts'].append({
                'type': 'email',
                'value': emails[0]
            })
        
        # Extract Australian phone numbers
        phone_patterns = [
            # Pattern: +61 format
            r'\+61\s*[0-9\s]{9,12}',
            # Pattern: 04xx xxx xxx (mobile)
            r'\b04\d{2}\s*\d{3}\s*\d{3}\b',
            # Pattern: (0x) xxxx xxxx (landline)
            r'\([0-9]{2}\)\s*[0-9]{4}\s*[0-9]{4}',
            # Pattern: 0x xxxx xxxx
            r'\b0[2-8]\s*[0-9]{4}\s*[0-9]{4}\b',
        ]
        
        for pattern in phone_patterns:
            phones = re.findall(pattern, text)
            if phones:
                # Clean up phone number
                phone = re.sub(r'\s+', ' ', phones[0].strip())
                extracted_info['phone'] = phone
                self.entity_threads['contacts'].append({
                    'type': 'phone',
                    'value': phone
                })
                break
        
        # Extract contact person names (look for patterns like "Contact: Name" or "Manager: Name")
        contact_patterns = [
            r'(?:Contact|Manager|Representative|Agent|Account Manager|Talent Manager):\s*([A-Z][a-zA-Z\s]{2,30})',
            r'([A-Z][a-zA-Z\s]{2,30})\s*-\s*(?:Manager|Agent|Representative|Contact)',
        ]
        
        for pattern in contact_patterns:
            matches = re.findall(pattern, text)
            if matches:
                contact_name = matches[0].strip()
                if len(contact_name.split()) <= 3:  # Reasonable name length
                    extracted_info['contact_person'] = contact_name
                    self.entity_threads['contacts'].append({
                        'type': 'contact_person',
                        'value': contact_name
                    })
                    break
    
    def _extract_address_information(self, text: str, extracted_info: Dict[str, str]) -> None:
        """Extract address information"""
        import re
        
        # Australian address patterns
        address_patterns = [
            # Pattern: "Level X, Street Number Street Name, Suburb, STATE postcode"
            r'(Level\s+\d+,\s*\d+[-\d]*\s+[A-Za-z\s]+(?:Street|St|Road|Rd|Avenue|Ave|Lane|Ln|Drive|Dr|Place|Pl|Court|Ct|Crescent|Cres),\s*[A-Za-z\s]+,\s*(?:NSW|VIC|QLD|WA|SA|TAS|ACT|NT)\s+\d{4})',
            # Pattern: "Street Number Street Name, Suburb STATE postcode"
            r'(\d+[-\d]*\s+[A-Za-z\s]+(?:Street|St|Road|Rd|Avenue|Ave|Lane|Ln|Drive|Dr|Place|Pl|Court|Ct|Crescent|Cres),\s*[A-Za-z\s]+\s+(?:NSW|VIC|QLD|WA|SA|TAS|ACT|NT)\s+\d{4})',
            # Pattern: "Suite/Level X, address"
            r'((?:Suite|Level)\s+\d+,\s*[^,]+,\s*[^,]+,\s*(?:NSW|VIC|QLD|WA|SA|TAS|ACT|NT)\s*\d{4})',
        ]
        
        for pattern in address_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                address = matches[0].strip()
                extracted_info['address'] = address
                self.entity_threads['locations'].append({
                    'type': 'address',
                    'value': address
                })
                break
    
    def _apply_entity_threading(self, extracted_info: Dict[str, str]) -> None:
        """Apply threading logic to ensure entity consistency across fields"""
        
        # Thread company names across related fields
        if extracted_info['brand_name'] != '[BRAND NAME]':
            # Use brand name for company and client if not already set
            if extracted_info['company_name'] == '[COMPANY NAME]':
                extracted_info['company_name'] = extracted_info['brand_name']
            if extracted_info['client_name'] == '[CLIENT NAME]':
                extracted_info['client_name'] = extracted_info['brand_name']
        
        # Thread individual names across related fields
        if extracted_info['influencer_name'] != '[INFLUENCER NAME]':
            if extracted_info['creator_name'] == '[CREATOR NAME]':
                extracted_info['creator_name'] = extracted_info['influencer_name']
            if extracted_info['partner_name'] == '[PARTNER NAME]':
                extracted_info['partner_name'] = extracted_info['influencer_name']
        
        # Thread location information
        locations = [item for item in self.entity_threads['locations'] if item['type'] in ['state', 'city', 'country']]
        if locations:
            # Ensure consistency between detected locations
            states = [loc['value'] for loc in locations if loc['type'] == 'state']
            cities = [loc['value'] for loc in locations if loc['type'] == 'city']
            
            # Use the most specific location information available
            if states and extracted_info['state'] == '[STATE]':
                extracted_info['state'] = states[0]
            if cities and extracted_info['city'] == '[CITY]':
                extracted_info['city'] = cities[0]
    
    def _validate_entity_consistency(self, extracted_info: Dict[str, str]) -> None:
        """Validate that extracted entities are consistent and make sense together"""
        
        # Validate that company names are reasonable
        company_fields = ['brand_name', 'company_name', 'client_name']
        for field in company_fields:
            if extracted_info[field] != f'[{field.upper().replace("_", " ")}]':
                # Check if it's a reasonable company name
                name = extracted_info[field]
                if len(name) < 2 or len(name) > 50:
                    extracted_info[field] = f'[{field.upper().replace("_", " ")}]'
                # Check for common non-company words
                invalid_words = ['the', 'and', 'or', 'but', 'with', 'for', 'to', 'from']
                if name.lower() in invalid_words:
                    extracted_info[field] = f'[{field.upper().replace("_", " ")}]'
        
        # Validate that individual names are reasonable
        individual_fields = ['influencer_name', 'creator_name', 'partner_name', 'contact_person']
        for field in individual_fields:
            if extracted_info[field] != f'[{field.upper().replace("_", " ")}]':
                name = extracted_info[field]
                # Individual names should be 2-4 words max
                name_parts = name.split()
                if len(name_parts) > 4 or len(name_parts) < 1:
                    extracted_info[field] = f'[{field.upper().replace("_", " ")}]'
                # Check for company suffixes in individual names
                company_suffixes = ['pty', 'ltd', 'llc', 'inc', 'corp', 'company']
                if any(suffix in name.lower() for suffix in company_suffixes):
                    extracted_info[field] = f'[{field.upper().replace("_", " ")}]'
        
        # Validate location consistency
        if extracted_info['state'] != '[STATE]' and extracted_info['country'] != '[COUNTRY]':
            # If we have an Australian state, country should be Australia
            australian_states = ['NSW', 'VIC', 'QLD', 'WA', 'SA', 'TAS', 'ACT', 'NT']
            if extracted_info['state'] in australian_states:
                extracted_info['country'] = 'Australia'
    
    def _build_threaded_location_string(self, extracted_info: Dict[str, str]) -> str:
        """Build a comprehensive location string using threaded information"""
        location_parts = []
        
        # Add specific address if available
        if extracted_info.get('address') and extracted_info['address'] != '[ADDRESS]':
            return f"of {extracted_info['address']}"
        
        # Build from city, state, country
        if extracted_info.get('city') and extracted_info['city'] != '[CITY]':
            location_parts.append(extracted_info['city'])
        
        if extracted_info.get('state') and extracted_info['state'] != '[STATE]':
            if extracted_info['state'] in ['NSW', 'VIC', 'QLD', 'WA', 'SA', 'TAS', 'ACT', 'NT']:
                # For Australian states, add "corporation" or "company"
                if location_parts:
                    return f"a company incorporated in {extracted_info['state']}, {extracted_info.get('country', 'Australia')}"
                else:
                    return f"a {extracted_info['state']} corporation"
            else:
                location_parts.append(extracted_info['state'])
        
        if extracted_info.get('country') and extracted_info['country'] != '[COUNTRY]':
            if extracted_info['country'] not in location_parts:
                location_parts.append(extracted_info['country'])
        
        if location_parts:
            return f"a company incorporated in {', '.join(location_parts)}"
        else:
            return "a corporation"
    
    def _build_threaded_entity_reference(self, extracted_info: Dict[str, str], entity_type: str) -> str:
        """Build entity reference with proper threading and validation"""
        entity_map = {
            'brand': extracted_info.get('brand_name', '[BRAND NAME]'),
            'company': extracted_info.get('company_name', '[COMPANY NAME]'),
            'client': extracted_info.get('client_name', '[CLIENT NAME]'),
            'influencer': extracted_info.get('influencer_name', '[INFLUENCER NAME]'),
            'creator': extracted_info.get('creator_name', '[CREATOR NAME]'),
            'partner': extracted_info.get('partner_name', '[PARTNER NAME]'),
            'contact': extracted_info.get('contact_person', '[CONTACT PERSON]')
        }
        
        entity_value = entity_map.get(entity_type, f'[{entity_type.upper()}]')
        
        # Return the threaded entity or a fallback
        if entity_value and not entity_value.startswith('['):
            return entity_value
        else:
            # Use threading to find alternative
            if entity_type in ['brand', 'company', 'client']:
                # Try other company fields
                for alt_type in ['brand', 'company', 'client']:
                    alt_value = entity_map.get(alt_type)
                    if alt_value and not alt_value.startswith('['):
                        return alt_value
            elif entity_type in ['influencer', 'creator', 'partner']:
                # Try other individual fields
                for alt_type in ['influencer', 'creator', 'partner']:
                    alt_value = entity_map.get(alt_type)
                    if alt_value and not alt_value.startswith('['):
                        return alt_value
            
            return entity_value

    def _generate_detailed_introduction(self, human_example: str, doc_type: str, style_preference: str) -> str:
        """Generate detailed introduction section with enhanced extracted information and threading"""
        extracted_info = self._extract_key_information(human_example)
        
        # Build location string with threading
        location_str = self._build_threaded_location_string(extracted_info)
        
        # Use threaded entity references
        brand_ref = self._build_threaded_entity_reference(extracted_info, 'brand')
        company_ref = self._build_threaded_entity_reference(extracted_info, 'company')
        client_ref = self._build_threaded_entity_reference(extracted_info, 'client')
        influencer_ref = self._build_threaded_entity_reference(extracted_info, 'influencer')
        creator_ref = self._build_threaded_entity_reference(extracted_info, 'creator')
        partner_ref = self._build_threaded_entity_reference(extracted_info, 'partner')
        
        if doc_type == "influencer":
            intro = f"This Influencer Marketing Agreement ('Agreement') is entered into between {brand_ref}, {location_str} ('Company'), and {influencer_ref}, an individual content creator ('Influencer'). This Agreement establishes the terms and conditions governing the professional relationship for digital marketing collaboration, content creation, and brand promotion activities across various social media platforms and digital channels."
        elif doc_type == "partnership":
            intro = f"This Brand Partnership Contract ('Contract') establishes a strategic alliance between {company_ref}, {location_str} ('Brand'), and {partner_ref} ('Partner'). This Contract governs all aspects of the collaborative relationship, including joint marketing initiatives, co-branded content development, cross-promotional activities, and shared business objectives designed to enhance market presence and drive mutual growth."
        elif doc_type == "content":
            intro = f"This Content Creation Agreement ('Agreement') is executed between {client_ref}, {location_str} ('Client'), and {creator_ref} ('Creator'). This Agreement defines the comprehensive framework for original content development, including creative services, intellectual property rights, content licensing, distribution permissions, and ongoing collaboration for digital marketing and promotional materials."
        else:
            intro = f"This Collaboration Agreement ('Agreement') establishes the working relationship between {brand_ref}, {location_str} ('First Party'), and {partner_ref} ('Second Party'). This Agreement outlines the terms, conditions, and expectations for professional collaboration, including project deliverables, performance standards, compensation structure, and mutual obligations throughout the duration of this partnership."
        
        return intro
    
    def _generate_detailed_scope_section(self, human_example: str, doc_type: str) -> str:
        """Generate detailed scope of work section"""
        example_lower = human_example.lower()
        
        scope_parts = ["SCOPE OF WORK AND SERVICES\n\n"]
        
        # Extract specific activities from the human example
        activities = []
        if 'post' in example_lower or 'content' in example_lower:
            activities.append("content creation and publishing")
        if 'video' in example_lower or 'reel' in example_lower:
            activities.append("video production and editing")
        if 'photo' in example_lower or 'image' in example_lower:
            activities.append("photography and visual content development")
        if 'story' in example_lower or 'stories' in example_lower:
            activities.append("social media story creation")
        if 'review' in example_lower:
            activities.append("product review and testimonial content")
        if 'event' in example_lower:
            activities.append("event coverage and live content")
        
        if not activities:
            activities = ["content creation", "brand promotion", "marketing collaboration"]
        
        scope_text = f"The scope of this engagement encompasses {', '.join(activities[:-1])}, and {activities[-1]}. " if len(activities) > 1 else f"The scope of this engagement encompasses {activities[0]}. "
        
        scope_text += f"All work shall be performed in accordance with industry best practices, brand guidelines, and applicable legal requirements. The scope includes strategic planning, creative development, content production, quality assurance, timely delivery, and performance optimization to achieve agreed-upon objectives and key performance indicators."
        
        scope_parts.append(scope_text)
        
        return "".join(scope_parts)
    
    def _generate_comprehensive_terms_section(self, human_example: str, doc_type: str) -> str:
        """Generate comprehensive terms and compensation section with extracted information"""
        extracted_info = self._extract_key_information(human_example)
        
        terms_parts = ["TERMS, COMPENSATION, AND PAYMENT STRUCTURE\n\n"]
        
        # Use extracted compensation or default structure
        if extracted_info['compensation'] != '[COMPENSATION]':
            compensation_text = f"Compensation for services rendered under this Agreement shall be {extracted_info['compensation']}, "
        else:
            compensation_text = "Compensation for services rendered under this Agreement shall be mutually agreed upon, "
        
        # Add duration if extracted
        if extracted_info['duration'] != '[DURATION]':
            duration_text = f"The term of this Agreement shall be {extracted_info['duration']} from the effective date. "
        else:
            duration_text = "The term of this Agreement shall be as mutually agreed upon by both parties. "
        
        compensation_text += "payable according to the following schedule: 50% upon execution of this Agreement and commencement of services, 25% upon completion of milestone deliverables, and 25% upon final completion and approval of all work products. "
        
        # Add deliverables if extracted
        if extracted_info['deliverables'] != '[DELIVERABLES]':
            deliverables_text = f"Specific deliverables include: {extracted_info['deliverables']}. "
        else:
            deliverables_text = "Specific deliverables shall be defined in the project scope. "
        
        terms_text = duration_text + compensation_text + deliverables_text + "Additional terms include: (a) All payments shall be made within thirty (30) days of invoice receipt; (b) Late payments may incur interest charges at the rate of 1.5% per month; (c) Expenses directly related to the project shall be reimbursed upon presentation of receipts; (d) Any changes to the scope of work must be agreed upon in writing and may result in adjusted compensation; (e) Performance bonuses may be available based on achievement of specified metrics and key performance indicators as mutually agreed upon by both parties."
        
        terms_parts.append(terms_text)
        
        return "".join(terms_parts)
    
    def _generate_rights_section(self, human_example: str, doc_type: str) -> str:
        """Generate rights and intellectual property section"""
        rights_text = "INTELLECTUAL PROPERTY RIGHTS AND USAGE PERMISSIONS\n\n"
        
        rights_text += "All original content created under this Agreement, including but not limited to text, images, videos, graphics, and other creative materials, shall be considered work-for-hire, with all rights, title, and interest vesting in the commissioning party upon full payment. The creator retains the right to use such content for portfolio purposes and professional promotion. "
        
        rights_text += "Usage rights include: (a) Perpetual, worldwide, royalty-free license to use, modify, distribute, and display the content; (b) Right to sublicense the content to third parties for marketing and promotional purposes; (c) Right to create derivative works based on the original content; (d) Attribution rights as mutually agreed upon. "
        
        rights_text += "Both parties agree to respect existing intellectual property rights and ensure all content is original or properly licensed. Any pre-existing intellectual property remains the property of its respective owner."
        
        return rights_text
    
    def _generate_compliance_section(self, doc_type: str) -> str:
        """Generate compliance and legal requirements section"""
        compliance_text = "COMPLIANCE AND LEGAL REQUIREMENTS\n\n"
        
        compliance_text += "Both parties agree to comply with all applicable federal, state, and local laws, regulations, and industry standards. This includes but is not limited to: (a) Federal Trade Commission (FTC) guidelines for advertising and endorsements; (b) Platform-specific terms of service and community guidelines; (c) Privacy laws and data protection regulations; (d) Copyright and trademark laws; (e) Consumer protection regulations. "
        
        compliance_text += "All sponsored content must include proper disclosures such as #ad, #sponsored, or #partnership as required by law. Both parties shall maintain appropriate insurance coverage and agree to indemnify each other against claims arising from breach of these compliance requirements."
        
        return compliance_text
    
    def _generate_termination_section(self, doc_type: str) -> str:
        """Generate termination and dispute resolution section"""
        termination_text = "TERMINATION AND DISPUTE RESOLUTION\n\n"
        
        termination_text += "This Agreement may be terminated: (a) By mutual written consent of both parties; (b) By either party with thirty (30) days written notice for convenience; (c) Immediately by either party for material breach that remains uncured after ten (10) days written notice; (d) Immediately for insolvency, bankruptcy, or assignment for benefit of creditors. "
        
        termination_text += "Upon termination, all work product completed shall be delivered, final payments made, and confidential information returned. Any disputes shall be resolved through binding arbitration in accordance with the rules of the American Arbitration Association. This Agreement shall be governed by the laws of [STATE] without regard to conflict of law principles."
        
        return termination_text
    
    def _generate_additional_clauses(self, human_example: str, doc_type: str, target_words: int) -> str:
        """Generate additional clauses to reach target length"""
        additional_text = "ADDITIONAL TERMS AND CONDITIONS\n\n"
        
        clauses = [
            "Force Majeure: Neither party shall be liable for any failure or delay in performance due to circumstances beyond their reasonable control, including but not limited to acts of God, natural disasters, war, terrorism, labor disputes, or government regulations.",
            
            "Confidentiality: Both parties acknowledge that they may have access to confidential and proprietary information. All such information shall be kept strictly confidential and not disclosed to third parties without prior written consent.",
            
            "Independent Contractor Relationship: The parties acknowledge that this Agreement creates an independent contractor relationship and not an employment, partnership, or joint venture relationship.",
            
            "Modification and Amendment: This Agreement may only be modified or amended by written instrument signed by both parties. No oral modifications shall be binding or enforceable.",
            
            "Severability: If any provision of this Agreement is deemed invalid or unenforceable, the remaining provisions shall continue in full force and effect.",
            
            "Entire Agreement: This Agreement constitutes the entire agreement between the parties and supersedes all prior negotiations, representations, or agreements relating to the subject matter hereof.",
            
            "Assignment: Neither party may assign this Agreement without the prior written consent of the other party, except that either party may assign this Agreement to an affiliate or in connection with a merger or sale of assets.",
            
            "Notices: All notices required under this Agreement shall be in writing and delivered by certified mail, email with delivery confirmation, or recognized courier service to the addresses specified herein."
        ]
        
        # Add clauses until we reach approximately the target word count
        current_words = len(additional_text.split())
        clause_index = 0
        
        while current_words < target_words and clause_index < len(clauses):
            additional_text += "\n\n" + clauses[clause_index]
            current_words = len(additional_text.split())
            clause_index += 1
        
        return additional_text
    
    def _generate_content_section(self, human_example: str, similar_templates: List[Dict]) -> str:
        """Generate comprehensive content requirements section with extracted information"""
        extracted_info = self._extract_key_information(human_example)
        example_lower = human_example.lower()
        
        content_text = "CONTENT REQUIREMENTS AND DELIVERABLES\n\n"
        
        # Use extracted platforms or detect from text
        if extracted_info['platforms'] != '[PLATFORMS]':
            platform_text = extracted_info['platforms']
        else:
            # Fallback to detection
            platforms = []
            if 'instagram' in example_lower:
                platforms.append('Instagram')
            if 'tiktok' in example_lower or 'tik tok' in example_lower:
                platforms.append('TikTok')
            if 'youtube' in example_lower:
                platforms.append('YouTube')
            if 'facebook' in example_lower:
                platforms.append('Facebook')
            if 'twitter' in example_lower or 'x.com' in example_lower:
                platforms.append('Twitter/X')
            if 'linkedin' in example_lower:
                platforms.append('LinkedIn')
            
            if not platforms:
                platforms = ['Instagram', 'TikTok', 'YouTube']  # Default
            
            platform_text = " and ".join(platforms) if len(platforms) <= 2 else ", ".join(platforms[:-1]) + ", and " + platforms[-1]
        
        # Content type identification
        content_types = []
        if 'post' in example_lower:
            content_types.append('feed posts')
        if 'story' in example_lower or 'stories' in example_lower:
            content_types.append('story content')
        if 'video' in example_lower:
            content_types.append('video content')
        if 'reel' in example_lower:
            content_types.append('short-form video reels')
        if 'review' in example_lower:
            content_types.append('product reviews')
        if 'tutorial' in example_lower:
            content_types.append('tutorial content')
        if 'unboxing' in example_lower:
            content_types.append('unboxing videos')
        
        if not content_types:
            content_types = ['feed posts', 'story content', 'video content']
        
        content_type_text = ", ".join(content_types[:-1]) + ", and " + content_types[-1] if len(content_types) > 1 else content_types[0]
        
        # Build comprehensive content requirements with enhanced threading
        brand_ref = self._build_threaded_entity_reference(extracted_info, 'brand')
        creator_ref = self._build_threaded_entity_reference(extracted_info, 'creator')
        
        # Use "the Brand/Creator" as fallback if no specific name found
        brand_display = brand_ref if not brand_ref.startswith('[') else "the Brand"
        creator_display = creator_ref if not creator_ref.startswith('[') else "the Creator"
        
        content_text += f"{creator_display} shall develop and publish original, high-quality content across {platform_text} platforms. Content deliverables include {content_type_text}, all featuring {brand_display}'s products or services in an authentic and engaging manner. "
        
        # Add specific deliverables if extracted
        if extracted_info['deliverables'] != '[DELIVERABLES]':
            content_text += f"Specific content requirements include: {extracted_info['deliverables']}. "
        
        content_text += "All content must comply with the following requirements: (a) Maintain professional quality standards for photography, videography, and written content; (b) Include proper brand attribution, mentions, and approved hashtags; (c) Adhere to platform-specific best practices and community guidelines; (d) Incorporate clear and compliant sponsored content disclosures; (e) Align with Brand guidelines while preserving the Creator's authentic voice and aesthetic. "
        
        content_text += f"Content creation process includes: initial concept approval, draft submission for review, incorporation of feedback, final approval before publication, and post-publication performance monitoring. {creator_display} agrees to respond professionally to comments and engage with audience interactions related to sponsored content within 24 hours of publication."
        
        return content_text
    
    
    def _generate_performance_section(self, human_example: str) -> str:
        """Generate comprehensive performance and metrics section"""
        example_lower = human_example.lower()
        
        performance_text = "PERFORMANCE METRICS AND REPORTING STANDARDS\n\n"
        
        # Identify relevant metrics from the example
        metrics = ["engagement rates", "reach", "impressions", "audience demographics"]
        if 'conversion' in example_lower or 'sales' in example_lower:
            metrics.append("conversion tracking and sales attribution")
        if 'code' in example_lower or 'discount' in example_lower:
            metrics.append("unique discount code performance")
        if 'click' in example_lower:
            metrics.append("click-through rates and link performance")
        if 'view' in example_lower:
            metrics.append("video view duration and completion rates")
        if 'share' in example_lower:
            metrics.append("content sharing and viral coefficient")
        
        metrics_text = ", ".join(metrics[:-1]) + ", and " + metrics[-1] if len(metrics) > 1 else metrics[0]
        
        performance_text += f"Campaign performance shall be evaluated using comprehensive analytics including {metrics_text}. Key performance indicators (KPIs) will be established at campaign initiation and monitored throughout the collaboration period. "
        
        performance_text += "Reporting requirements include: (a) Weekly performance summaries with key metrics and insights; (b) Monthly comprehensive reports with trend analysis and optimization recommendations; (c) Real-time access to campaign dashboards and analytics platforms; (d) Post-campaign analysis with ROI calculations and learnings documentation. "
        
        performance_text += "Both parties commit to transparent data sharing, collaborative performance optimization, and continuous improvement of campaign strategies. Minimum performance thresholds may be established with corresponding adjustment mechanisms for underperforming content."
        
        return performance_text

# Auto-detection functions
def detect_document_type(text: str) -> tuple[str, float, str]:
    """Detect document type based on text content"""
    text_lower = text.lower()
    
    # Keywords and patterns for different document types
    patterns = {
        "influencer_agreement": {
            "keywords": ["influencer", "instagram", "tiktok", "youtube", "social media", "post", "story", "content creator", "follower", "engagement", "brand ambassador", "sponsored", "collaboration"],
            "phrases": ["social media", "content creation", "brand partnership", "promotional content", "hashtag"]
        },
        "brand_partnership": {
            "keywords": ["brand", "partnership", "marketing", "promotion", "campaign", "sponsor", "advertise", "collaborate", "co-brand", "joint venture"],
            "phrases": ["brand partnership", "marketing campaign", "promotional activities", "joint marketing"]
        },
        "content_creation": {
            "keywords": ["content", "article", "blog", "video", "podcast", "write", "create", "produce", "publish", "editorial", "freelance", "writer"],
            "phrases": ["content creation", "article writing", "video production", "blog post", "editorial content"]
        },
        "marketing_agreement": {
            "keywords": ["marketing", "advertise", "promote", "campaign", "media", "advertising", "publicity", "pr", "public relations"],
            "phrases": ["marketing services", "advertising campaign", "promotional activities", "media placement"]
        },
        "legal_template": {
            "keywords": ["contract", "agreement", "terms", "conditions", "legal", "clause", "provision", "liability", "indemnity", "jurisdiction"],
            "phrases": ["legal agreement", "terms and conditions", "contractual obligations", "legal framework"]
        }
    }
    
    scores = {}
    reasoning = {}
    
    for doc_type, pattern_data in patterns.items():
        score = 0
        matches = []
        
        # Check keywords
        for keyword in pattern_data["keywords"]:
            if keyword in text_lower:
                score += 1
                matches.append(keyword)
        
        # Check phrases (weighted higher)
        for phrase in pattern_data["phrases"]:
            if phrase in text_lower:
                score += 2
                matches.append(f'"{phrase}"')
        
        # Normalize score
        total_possible = len(pattern_data["keywords"]) + (len(pattern_data["phrases"]) * 2)
        normalized_score = score / total_possible if total_possible > 0 else 0
        
        scores[doc_type] = normalized_score
        reasoning[doc_type] = f"Matched: {', '.join(matches[:5])}" if matches else "No matches"
    
    # Get the highest scoring type
    best_type = max(scores.keys(), key=lambda k: scores[k])
    confidence = scores[best_type]
    
    return best_type, confidence, reasoning[best_type]

def detect_style_preference(text: str) -> tuple[str, float, str]:
    """Detect style preference based on text content and complexity"""
    text_lower = text.lower()
    
    # Style indicators
    formal_indicators = ["shall", "hereby", "whereas", "therefore", "pursuant", "aforementioned", "heretofore", "notwithstanding"]
    business_indicators = ["we", "our", "company", "business", "professional", "service", "client", "customer"]
    detailed_indicators = ["specific", "detailed", "comprehensive", "thorough", "complete", "extensive", "particular"]
    
    # Count indicators
    formal_count = sum(1 for indicator in formal_indicators if indicator in text_lower)
    business_count = sum(1 for indicator in business_indicators if indicator in text_lower)
    detailed_count = sum(1 for indicator in detailed_indicators if indicator in text_lower)
    
    # Analyze sentence complexity
    sentences = text.split('.')
    avg_sentence_length = sum(len(s.split()) for s in sentences) / len(sentences) if sentences else 0
    
    # Determine style
    if formal_count > 2 or avg_sentence_length > 25:
        return "formal", 0.8, f"Formal language detected ({formal_count} formal terms, avg {avg_sentence_length:.1f} words/sentence)"
    elif detailed_count > 2 or len(text) > 800:
        return "detailed", 0.7, f"Detailed content detected ({detailed_count} detail indicators, {len(text)} characters)"
    elif business_count > 3:
        return "business", 0.7, f"Business language detected ({business_count} business terms)"
    else:
        return "professional", 0.6, "Default professional style (balanced approach)"

def detect_target_length(text: str) -> tuple[int, float, str]:
    """Detect appropriate target length based on input complexity and content"""
    word_count = len(text.split())
    char_count = len(text)
    
    # Complexity indicators
    complex_terms = ["liability", "indemnification", "jurisdiction", "arbitration", "intellectual property", "confidentiality", "non-disclosure", "termination", "breach"]
    complexity_score = sum(1 for term in complex_terms if term.lower() in text.lower())
    
    # Sentence complexity
    sentences = text.split('.')
    avg_sentence_length = sum(len(s.split()) for s in sentences) / len(sentences) if sentences else 0
    
    # Determine target length
    if word_count < 50:
        target = 500
        confidence = 0.6
        reason = f"Short input ({word_count} words) suggests concise output"
    elif word_count < 150:
        if complexity_score > 3 or avg_sentence_length > 20:
            target = 1000
            confidence = 0.8
            reason = f"Medium input with high complexity ({complexity_score} complex terms)"
        else:
            target = 700
            confidence = 0.7
            reason = f"Medium input ({word_count} words) suggests standard length"
    elif word_count < 300:
        if complexity_score > 5:
            target = 1200
            confidence = 0.9
            reason = f"Long input with high complexity ({complexity_score} complex terms)"
        else:
            target = 1000
            confidence = 0.8
            reason = f"Long input ({word_count} words) suggests comprehensive output"
    else:
        target = 1200
        confidence = 0.9
        reason = f"Very long input ({word_count} words) requires comprehensive treatment"
    
    return target, confidence, reason

def auto_detect_parameters(text: str) -> Dict[str, Any]:
    """Auto-detect all parameters for text generation"""
    start_time = time.time()
    
    # Detect each parameter
    doc_type, doc_confidence, doc_reasoning = detect_document_type(text)
    style, style_confidence, style_reasoning = detect_style_preference(text)
    length, length_confidence, length_reasoning = detect_target_length(text)
    
    processing_time = time.time() - start_time
    
    return {
        "target_length": length,
        "style_preference": style,
        "document_type": doc_type,
        "confidence_scores": {
            "target_length": length_confidence,
            "style_preference": style_confidence,
            "document_type": doc_confidence,
            "overall": (length_confidence + style_confidence + doc_confidence) / 3
        },
        "reasoning": {
            "target_length": length_reasoning,
            "style_preference": style_reasoning,
            "document_type": doc_reasoning
        },
        "processing_time": processing_time
    }

# Initialize model service (conditionally)
model_service = None

def get_model_service():
    """Get or initialize model service"""
    global model_service
    if model_service is None:
        model_service = ModelService()
    return model_service

# API Endpoints
@app.get("/health", response_model=HealthResponse)
async def health():
    """Health check endpoint"""
    # Always return healthy for basic server functionality
    if not HAS_ML_DEPS:
        return HealthResponse(
            status="healthy",
            model_loaded=False,
            model_path="N/A - ML dependencies not installed",
            model_dimension=None,
            uptime_seconds=time.time() - start_time
        )
    
    # Try to get model service, but don't fail if it can't load
    try:
        ms = get_model_service()
        return HealthResponse(
            status="healthy",  # Always healthy for server
            model_loaded=ms.model is not None,
            model_path=ms.model_path,
            model_dimension=ms.model.get_sentence_embedding_dimension() if ms.model else None,
            uptime_seconds=time.time() - start_time
        )
    except Exception as e:
        logger.error(f"Health check error: {e}")
        return HealthResponse(
            status="healthy",  # Server is healthy even if model fails
            model_loaded=False,
            model_path=f"Error: {str(e)}",
            model_dimension=None,
            uptime_seconds=time.time() - start_time
        )

@app.get("/status")
async def status():
    """Simple status endpoint for debugging"""
    return {
        "status": "running",
        "timestamp": time.time(),
        "uptime": time.time() - start_time,
        "has_ml_deps": HAS_ML_DEPS,
        "has_numpy": HAS_NUMPY,
        "environment": ENV,
        "port": PORT,
        "host": HOST
    }

@app.post("/embed", response_model=EmbedResponse)
async def embed(request: EmbedRequest):
    """Generate embeddings for texts"""
    start_time_req = time.time()
    
    try:
        embeddings = model_service.encode_texts(request.texts, request.normalize)
        processing_time = time.time() - start_time_req
        
        return EmbedResponse(
            embeddings=embeddings.tolist(),
            processing_time=processing_time,
            texts_count=len(request.texts)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/similarity", response_model=SimilarityResponse)
async def similarity(request: SimilarityRequest):
    """Compute similarity between two texts"""
    start_time_req = time.time()
    
    try:
        sim_score = model_service.compute_similarity(request.text1, request.text2)
        processing_time = time.time() - start_time_req
        
        # Interpretation
        if sim_score > 0.8:
            interpretation = "Very similar"
        elif sim_score > 0.6:
            interpretation = "Moderately similar"
        elif sim_score > 0.4:
            interpretation = "Somewhat similar"
        else:
            interpretation = "Different"
        
        return SimilarityResponse(
            similarity=sim_score,
            interpretation=interpretation,
            processing_time=processing_time
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/search", response_model=SearchResponse)
async def search(request: SearchRequest):
    """Search for similar documents"""
    start_time_req = time.time()
    
    try:
        results = model_service.search_similar(
            request.query, 
            request.documents, 
            request.top_k
        )
        processing_time = time.time() - start_time_req
        
        return SearchResponse(
            results=results,
            query=request.query,
            processing_time=processing_time
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/analyze", response_model=AnalyzeResponse)
async def analyze(request: AnalyzeRequest):
    """Analyze content for specific patterns"""
    start_time_req = time.time()
    
    try:
        analysis = model_service.analyze_content(request.content, request.analyze_type)
        processing_time = time.time() - start_time_req
        
        return AnalyzeResponse(
            analysis=analysis,
            processing_time=processing_time
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/generate", response_model=GenerateResponse)
async def generate(request: GenerateRequest):
    """Generate similar legal text based on human example"""
    start_time_req = time.time()
    
    try:
        result = model_service.generate_similar_text(
            request.human_example,
            request.target_length,
            request.style_preference,
            request.document_type
        )
        processing_time = time.time() - start_time_req
        
        return GenerateResponse(
            generated_text=result["generated_text"],
            similarity_to_example=result["similarity_to_example"],
            word_count=result["word_count"],
            processing_time=processing_time,
            generation_metadata=result["generation_metadata"]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/model/info")
async def model_info():
    """Get model information"""
    if not model_service.model:
        raise HTTPException(status_code=500, detail="Model not loaded")
    
    # Load training results if available
    training_results = {}
    try:
        results_path = Path(model_service.model_path) / "evaluation_results.json"
        if results_path.exists():
            with open(results_path, 'r') as f:
                training_results = json.load(f)
    except Exception as e:
        logger.warning(f"Could not load training results: {e}")
    
    return {
        "model_path": model_service.model_path,
        "dimension": model_service.model.get_sentence_embedding_dimension(),
        "training_results": training_results,
        "status": "ready"
    }

@app.post("/batch/generate")
async def batch_generate(request: BatchGenerateRequest, background_tasks: BackgroundTasks):
    """Start batch generation process"""
    batch_id = str(uuid.uuid4())
    
    # Initialize batch job
    batch_jobs[batch_id] = {
        "batch_id": batch_id,
        "status": "processing",
        "total_items": len(request.batch_inputs),
        "completed_items": 0,
        "results": [],
        "created_at": datetime.now().isoformat(),
        "completed_at": None,
        "batch_name": request.batch_name
    }
    
    # Start background processing
    background_tasks.add_task(process_batch_generation, batch_id, request.batch_inputs)
    
    return {"batch_id": batch_id, "status": "processing", "message": "Batch processing started"}

@app.get("/batch/status/{batch_id}")
async def get_batch_status(batch_id: str):
    """Get batch processing status"""
    if batch_id not in batch_jobs:
        raise HTTPException(status_code=404, detail="Batch job not found")
    
    return batch_jobs[batch_id]

@app.get("/batch/download/{batch_id}")
async def download_batch_results(batch_id: str):
    """Download batch results as ZIP file containing .txt files"""
    if batch_id not in batch_jobs:
        raise HTTPException(status_code=404, detail="Batch job not found")
    
    batch_job = batch_jobs[batch_id]
    if batch_job["status"] != "completed":
        raise HTTPException(status_code=400, detail="Batch processing not completed yet")
    
    from fastapi.responses import StreamingResponse
    
    # Create ZIP file in memory
    zip_buffer = io.BytesIO()
    
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        # Add batch info file
        batch_info = f"""Batch Processing Results
========================

Batch ID: {batch_id}
Batch Name: {batch_job['batch_name']}
Total Items: {batch_job['total_items']}
Created: {batch_job['created_at']}
Completed: {batch_job['completed_at']}

Generated by Thinkerbell Legal Text Generator
"""
        zip_file.writestr("00_batch_info.txt", batch_info)
        
        # Add each result as a separate .txt file
        for i, result in enumerate(batch_job["results"], 1):
            # Create filename with zero-padded number
            filename = f"{i:02d}_legal_document_{result.get('document_type', 'template')}.txt"
            
            # Create content with metadata header
            content = f"""Legal Document Generated by Thinkerbell
==========================================

Document Type: {result.get('document_type', 'Legal Template')}
Style: {result.get('style_preference', 'Professional')}
Target Length: {result.get('target_length', 'N/A')} words
Generated: {result.get('generated_at', 'N/A')}

Original Input:
--------------
{result.get('human_example', 'N/A')}

Generated Legal Text:
--------------------
{result.get('generated_text', 'No content available')}

Performance Metrics:
-------------------
Word Count: {result.get('word_count', 'N/A')}
Similarity Score: {result.get('similarity_to_example', 'N/A')}
Processing Time: {result.get('processing_time', 'N/A')}ms
"""
            zip_file.writestr(filename, content)
    
    zip_buffer.seek(0)
    
    # Create filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"thinkerbell_batch_{batch_job['batch_name'].replace(' ', '_')}_{timestamp}.zip"
    
    return StreamingResponse(
        io.BytesIO(zip_buffer.read()),
        media_type="application/zip",
        headers={
            "Content-Disposition": f"attachment; filename={filename}"
        }
    )

@app.get("/batch/list")
async def list_batch_jobs():
    """List all batch jobs"""
    return {
        "batch_jobs": [
            {
                "batch_id": job_id,
                "batch_name": job["batch_name"],
                "status": job["status"],
                "total_items": job["total_items"],
                "completed_items": job["completed_items"],
                "created_at": job["created_at"],
                "completed_at": job.get("completed_at")
            }
            for job_id, job in batch_jobs.items()
        ]
    }

@app.post("/auto-detect", response_model=AutoDetectResponse)
async def auto_detect_text_parameters(request: AutoDetectRequest):
    """Auto-detect target length, style, and document type from input text"""
    try:
        if not request.text or len(request.text.strip()) < 10:
            raise HTTPException(status_code=400, detail="Text must be at least 10 characters long")
        
        # Perform auto-detection
        detection_result = auto_detect_parameters(request.text)
        
        return AutoDetectResponse(
            target_length=detection_result["target_length"],
            style_preference=detection_result["style_preference"],
            document_type=detection_result["document_type"],
            confidence_scores=detection_result["confidence_scores"],
            reasoning=detection_result["reasoning"]
        )
        
    except Exception as e:
        logger.error(f"Auto-detection error: {e}")
        raise HTTPException(status_code=500, detail=f"Auto-detection failed: {str(e)}")

async def process_batch_generation(batch_id: str, batch_inputs: List[Dict[str, Any]]):
    """Background task to process batch generation"""
    try:
        batch_job = batch_jobs[batch_id]
        
        for i, input_data in enumerate(batch_inputs):
            try:
                # Convert dict to GenerateRequest-like object
                human_example = input_data.get("human_example", "")
                target_length = input_data.get("target_length", 700)
                style_preference = input_data.get("style_preference", "professional")
                document_type = input_data.get("document_type", "legal_template")
                
                # Generate text
                result = model_service.generate_similar_text(
                    human_example, target_length, style_preference, document_type
                )
                
                # Add input info to result
                result["input_index"] = i
                result["input_data"] = input_data
                
                batch_job["results"].append(result)
                batch_job["completed_items"] = i + 1
                
            except Exception as e:
                # Add error result
                error_result = {
                    "input_index": i,
                    "input_data": input_data,
                    "error": str(e),
                    "generated_text": "",
                    "similarity_to_example": 0.0,
                    "word_count": 0,
                    "generation_metadata": {"error": True}
                }
                batch_job["results"].append(error_result)
                batch_job["completed_items"] = i + 1
        
        # Mark as completed
        batch_job["status"] = "completed"
        batch_job["completed_at"] = datetime.now().isoformat()
        
    except Exception as e:
        batch_job["status"] = "failed"
        batch_job["error"] = str(e)
        batch_job["completed_at"] = datetime.now().isoformat()

@app.get("/")
async def root():
    """Root endpoint"""
    try:
        ms = get_model_service() if HAS_ML_DEPS else None
        model_loaded = ms.model is not None if ms else False
    except:
        model_loaded = False
        
    return {
        "message": "Thinkerbell Enhanced API",
        "version": "2.0.0",
        "model_loaded": model_loaded,
        "ml_dependencies": HAS_ML_DEPS,
        "endpoints": [
            "/health", "/embed", "/similarity", "/search", "/analyze", "/generate", "/model/info",
            "/batch/generate", "/batch/status/{batch_id}", "/batch/download/{batch_id}", "/batch/list",
            "/auto-detect"
        ]
    }

# Serve frontend for all non-API routes
@app.get("/app")
@app.get("/app/{path:path}")
async def serve_frontend(path: str = ""):
    """Serve the frontend application"""
    static_file = Path("static/index.html")
    if static_file.exists():
        return FileResponse("static/index.html")
    else:
        return {"message": "Frontend not available", "api_available": True}

def main():
    """Main function to run the server"""
    logger.info(f"Starting Thinkerbell Enhanced API server...")
    logger.info(f"Model path: {MODEL_DIR}")
    logger.info(f"Server will run on {HOST}:{PORT}")
    
    if not HAS_ML_DEPS:
        logger.warning("ML dependencies not available. Server will start in basic mode.")
        logger.info("ML endpoints will attempt to install dependencies on first use.")
    else:
        logger.info("ML dependencies available. Model will be loaded on first use.")
    
    # Always start the server - it can handle missing dependencies gracefully
    uvicorn.run(
        "backend_api_server:app",
        host=HOST,
        port=PORT,
        reload=False,
        log_level="info"
    )

if __name__ == "__main__":
    main()

