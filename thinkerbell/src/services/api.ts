/**
 * API Service Layer for Thinkerbell Frontend
 * Handles all communication with the backend API
 */

const API_BASE_URL = 'http://localhost:8000';

export interface EmbedRequest {
  texts: string[];
  normalize?: boolean;
}

export interface SimilarityRequest {
  text1: string;
  text2: string;
}

export interface SearchRequest {
  query: string;
  documents: string[];
  top_k?: number;
}

export interface AnalyzeRequest {
  content: string;
  analyze_type?: string;
}

export interface GenerateRequest {
  human_example: string;
  target_length?: number;
  style_preference?: string;
  document_type?: string;
}

export interface HealthResponse {
  status: string;
  model_loaded: boolean;
  model_path: string;
  model_dimension?: number;
  uptime_seconds: number;
}

export interface EmbedResponse {
  embeddings: number[][];
  processing_time: number;
  texts_count: number;
}

export interface SimilarityResponse {
  similarity: number;
  interpretation: string;
  processing_time: number;
}

export interface SearchResponse {
  results: Array<{
    document_index: number;
    document: string;
    similarity: number;
    preview: string;
  }>;
  query: string;
  processing_time: number;
}

export interface AnalyzeResponse {
  analysis: {
    content_length: number;
    word_count: number;
    sentence_count: number;
    analyze_type: string;
    embedding_stats: {
      dimension: number;
      mean: number;
      std: number;
      min: number;
      max: number;
    };
    agreement_features?: {
      has_brand_terms: boolean;
      has_content_terms: boolean;
      has_legal_terms: boolean;
      has_timeline_terms: boolean;
      brand_term_count: number;
      content_term_count: number;
      legal_term_count: number;
      timeline_term_count: number;
      agreement_score: number;
    };
  };
  processing_time: number;
}

export interface GenerateResponse {
  generated_text: string;
  similarity_to_example: number;
  word_count: number;
  processing_time: number;
  generation_metadata: {
    style_preference: string;
    document_type: string;
    reference_templates_used: number;
    target_length: number;
    actual_length: number;
  };
}

class ApiService {
  private baseUrl: string;

  constructor(baseUrl: string = API_BASE_URL) {
    this.baseUrl = baseUrl;
  }

  private async request<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
    const url = `${this.baseUrl}${endpoint}`;
    
    const defaultOptions: RequestInit = {
      headers: {
        'Content-Type': 'application/json',
      },
    };

    const response = await fetch(url, { ...defaultOptions, ...options });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.detail || `HTTP ${response.status}: ${response.statusText}`);
    }

    return response.json();
  }

  async health(): Promise<HealthResponse> {
    return this.request<HealthResponse>('/health');
  }

  async embed(request: EmbedRequest): Promise<EmbedResponse> {
    return this.request<EmbedResponse>('/embed', {
      method: 'POST',
      body: JSON.stringify(request),
    });
  }

  async similarity(request: SimilarityRequest): Promise<SimilarityResponse> {
    return this.request<SimilarityResponse>('/similarity', {
      method: 'POST',
      body: JSON.stringify(request),
    });
  }

  async search(request: SearchRequest): Promise<SearchResponse> {
    return this.request<SearchResponse>('/search', {
      method: 'POST',
      body: JSON.stringify(request),
    });
  }

  async analyze(request: AnalyzeRequest): Promise<AnalyzeResponse> {
    return this.request<AnalyzeResponse>('/analyze', {
      method: 'POST',
      body: JSON.stringify(request),
    });
  }

  async getModelInfo(): Promise<any> {
    return this.request('/model/info');
  }

  async generate(request: GenerateRequest): Promise<GenerateResponse> {
    return this.request<GenerateResponse>('/generate', {
      method: 'POST',
      body: JSON.stringify(request),
    });
  }

  async getRoot(): Promise<any> {
    return this.request('/');
  }
}

export const apiService = new ApiService();
export default apiService;

