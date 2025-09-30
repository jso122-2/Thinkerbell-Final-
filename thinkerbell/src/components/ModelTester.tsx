import React, { useState, useEffect } from 'react';
import apiService, { HealthResponse, SimilarityResponse, SearchResponse, AnalyzeResponse } from '../services/api';

interface ModelTesterProps {
  className?: string;
}

const ModelTester: React.FC<ModelTesterProps> = ({ className = '' }) => {
  const [health, setHealth] = useState<HealthResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<'similarity' | 'search' | 'analyze'>('similarity');

  // Similarity test state
  const [text1, setText1] = useState('');
  const [text2, setText2] = useState('');
  const [similarityResult, setSimilarityResult] = useState<SimilarityResponse | null>(null);

  // Search test state
  const [query, setQuery] = useState('');
  const [documents, setDocuments] = useState<string[]>(['']);
  const [searchResult, setSearchResult] = useState<SearchResponse | null>(null);

  // Analysis test state
  const [content, setContent] = useState('');
  const [analyzeResult, setAnalyzeResult] = useState<AnalyzeResponse | null>(null);

  useEffect(() => {
    checkHealth();
  }, []);

  const checkHealth = async () => {
    try {
      const healthData = await apiService.health();
      setHealth(healthData);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to connect to API');
    }
  };

  const testSimilarity = async () => {
    if (!text1.trim() || !text2.trim()) {
      setError('Please enter both texts');
      return;
    }

    setLoading(true);
    setError(null);
    
    try {
      const result = await apiService.similarity({ text1, text2 });
      setSimilarityResult(result);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Similarity test failed');
    } finally {
      setLoading(false);
    }
  };

  const testSearch = async () => {
    if (!query.trim()) {
      setError('Please enter a search query');
      return;
    }

    const validDocs = documents.filter(doc => doc.trim());
    if (validDocs.length === 0) {
      setError('Please enter at least one document');
      return;
    }

    setLoading(true);
    setError(null);
    
    try {
      const result = await apiService.search({ 
        query, 
        documents: validDocs,
        top_k: 5 
      });
      setSearchResult(result);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Search test failed');
    } finally {
      setLoading(false);
    }
  };

  const testAnalyze = async () => {
    if (!content.trim()) {
      setError('Please enter content to analyze');
      return;
    }

    setLoading(true);
    setError(null);
    
    try {
      const result = await apiService.analyze({ 
        content,
        analyze_type: 'influencer_agreement'
      });
      setAnalyzeResult(result);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Analysis failed');
    } finally {
      setLoading(false);
    }
  };

  const addDocument = () => {
    setDocuments([...documents, '']);
  };

  const updateDocument = (index: number, value: string) => {
    const newDocs = [...documents];
    newDocs[index] = value;
    setDocuments(newDocs);
  };

  const removeDocument = (index: number) => {
    if (documents.length > 1) {
      setDocuments(documents.filter((_, i) => i !== index));
    }
  };

  const loadSampleData = () => {
    if (activeTab === 'similarity') {
      setText1('This influencer marketing agreement establishes terms for brand collaboration with content creation requirements and usage rights for 90 days.');
      setText2('Brand partnership contract for social media promotion including Instagram posts, stories, and reels with exclusive content for 60 days.');
    } else if (activeTab === 'search') {
      setQuery('brand collaboration agreement');
      setDocuments([
        'This influencer marketing agreement establishes terms for brand collaboration with content creation requirements and usage rights for 90 days.',
        'Brand partnership contract for social media promotion including Instagram posts, stories, and reels with exclusive content for 60 days.',
        'Influencer collaboration agreement for product review and unboxing content with non-exclusive usage rights and performance metrics tracking.',
        'Social media marketing contract for lifestyle brand featuring authentic content creation and audience engagement requirements.',
        'Digital marketing partnership for fashion brand including outfit styling, product photography, and brand mention obligations.'
      ]);
    } else if (activeTab === 'analyze') {
      setContent('BRAND COLLABORATION AGREEMENT\n\nThis agreement between [Brand] and [Influencer] establishes the terms for a social media marketing partnership. The influencer agrees to create authentic content featuring the brand\'s products across Instagram and TikTok platforms. Content must include brand mentions, product tags, and usage of provided hashtags. The collaboration period is 60 days with exclusive content rights. Compensation includes monetary payment and product gifting. Performance metrics will be tracked including engagement rates, reach, and conversion tracking through unique discount codes.');
    }
  };

  return (
    <div className={`bg-gray-900 text-white p-6 rounded-lg ${className}`}>
      {/* Header */}
      <div className="mb-6">
        <h2 className="text-2xl font-bold mb-2">🧠 Model Tester</h2>
        
        {/* Health Status */}
        <div className="flex items-center gap-4 mb-4">
          <button 
            onClick={checkHealth}
            className="px-3 py-1 bg-blue-600 hover:bg-blue-700 rounded text-sm"
          >
            Check Health
          </button>
          
          {health && (
            <div className="flex items-center gap-2">
              <div className={`w-3 h-3 rounded-full ${health.model_loaded ? 'bg-green-500' : 'bg-red-500'}`}></div>
              <span className="text-sm">
                {health.model_loaded ? 'Model Ready' : 'Model Not Loaded'} 
                {health.model_dimension && ` (${health.model_dimension}D)`}
              </span>
            </div>
          )}
        </div>

        {error && (
          <div className="bg-red-600 text-white p-3 rounded mb-4">
            {error}
          </div>
        )}
      </div>

      {/* Tabs */}
      <div className="flex gap-2 mb-6">
        {(['similarity', 'search', 'analyze'] as const).map((tab) => (
          <button
            key={tab}
            onClick={() => setActiveTab(tab)}
            className={`px-4 py-2 rounded capitalize ${
              activeTab === tab 
                ? 'bg-blue-600 text-white' 
                : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
            }`}
          >
            {tab}
          </button>
        ))}
        
        <button
          onClick={loadSampleData}
          className="px-4 py-2 bg-green-600 hover:bg-green-700 rounded text-sm ml-auto"
        >
          Load Sample Data
        </button>
      </div>

      {/* Similarity Tab */}
      {activeTab === 'similarity' && (
        <div className="space-y-4">
          <h3 className="text-lg font-semibold">🔍 Text Similarity</h3>
          
          <div>
            <label className="block text-sm font-medium mb-2">Text 1:</label>
            <textarea
              value={text1}
              onChange={(e) => setText1(e.target.value)}
              className="w-full p-3 bg-gray-800 border border-gray-600 rounded resize-none"
              rows={3}
              placeholder="Enter first text..."
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium mb-2">Text 2:</label>
            <textarea
              value={text2}
              onChange={(e) => setText2(e.target.value)}
              className="w-full p-3 bg-gray-800 border border-gray-600 rounded resize-none"
              rows={3}
              placeholder="Enter second text..."
            />
          </div>
          
          <button
            onClick={testSimilarity}
            disabled={loading}
            className="px-6 py-2 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-600 rounded"
          >
            {loading ? 'Computing...' : 'Compare Similarity'}
          </button>
          
          {similarityResult && (
            <div className="bg-gray-800 p-4 rounded">
              <h4 className="font-semibold mb-2">Results:</h4>
              <div className="space-y-2">
                <div className="flex justify-between">
                  <span>Similarity Score:</span>
                  <span className="font-mono">{similarityResult.similarity.toFixed(4)}</span>
                </div>
                <div className="flex justify-between">
                  <span>Interpretation:</span>
                  <span className={`font-semibold ${
                    similarityResult.similarity > 0.8 ? 'text-green-400' :
                    similarityResult.similarity > 0.6 ? 'text-yellow-400' :
                    similarityResult.similarity > 0.4 ? 'text-orange-400' : 'text-red-400'
                  }`}>
                    {similarityResult.interpretation}
                  </span>
                </div>
                <div className="flex justify-between text-sm text-gray-400">
                  <span>Processing Time:</span>
                  <span>{(similarityResult.processing_time * 1000).toFixed(1)}ms</span>
                </div>
              </div>
            </div>
          )}
        </div>
      )}

      {/* Search Tab */}
      {activeTab === 'search' && (
        <div className="space-y-4">
          <h3 className="text-lg font-semibold">🔎 Document Search</h3>
          
          <div>
            <label className="block text-sm font-medium mb-2">Search Query:</label>
            <input
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              className="w-full p-3 bg-gray-800 border border-gray-600 rounded"
              placeholder="Enter search query..."
            />
          </div>
          
          <div>
            <div className="flex justify-between items-center mb-2">
              <label className="text-sm font-medium">Documents:</label>
              <button
                onClick={addDocument}
                className="px-3 py-1 bg-green-600 hover:bg-green-700 rounded text-sm"
              >
                Add Document
              </button>
            </div>
            
            {documents.map((doc, index) => (
              <div key={index} className="flex gap-2 mb-2">
                <textarea
                  value={doc}
                  onChange={(e) => updateDocument(index, e.target.value)}
                  className="flex-1 p-2 bg-gray-800 border border-gray-600 rounded resize-none"
                  rows={2}
                  placeholder={`Document ${index + 1}...`}
                />
                {documents.length > 1 && (
                  <button
                    onClick={() => removeDocument(index)}
                    className="px-2 py-1 bg-red-600 hover:bg-red-700 rounded text-sm"
                  >
                    ×
                  </button>
                )}
              </div>
            ))}
          </div>
          
          <button
            onClick={testSearch}
            disabled={loading}
            className="px-6 py-2 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-600 rounded"
          >
            {loading ? 'Searching...' : 'Search Documents'}
          </button>
          
          {searchResult && (
            <div className="bg-gray-800 p-4 rounded">
              <h4 className="font-semibold mb-2">Search Results:</h4>
              <div className="text-sm text-gray-400 mb-3">
                Query: "{searchResult.query}" | Processing: {(searchResult.processing_time * 1000).toFixed(1)}ms
              </div>
              
              <div className="space-y-3">
                {searchResult.results.map((result, index) => (
                  <div key={index} className="border-l-4 border-blue-500 pl-3">
                    <div className="flex justify-between items-start mb-1">
                      <span className="text-sm font-semibold">Document {result.document_index + 1}</span>
                      <span className="text-sm font-mono text-green-400">
                        {result.similarity.toFixed(3)}
                      </span>
                    </div>
                    <p className="text-sm text-gray-300">{result.preview}</p>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}

      {/* Analyze Tab */}
      {activeTab === 'analyze' && (
        <div className="space-y-4">
          <h3 className="text-lg font-semibold">📊 Content Analysis</h3>
          
          <div>
            <label className="block text-sm font-medium mb-2">Content to Analyze:</label>
            <textarea
              value={content}
              onChange={(e) => setContent(e.target.value)}
              className="w-full p-3 bg-gray-800 border border-gray-600 rounded resize-none"
              rows={6}
              placeholder="Enter content to analyze..."
            />
          </div>
          
          <button
            onClick={testAnalyze}
            disabled={loading}
            className="px-6 py-2 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-600 rounded"
          >
            {loading ? 'Analyzing...' : 'Analyze Content'}
          </button>
          
          {analyzeResult && (
            <div className="bg-gray-800 p-4 rounded">
              <h4 className="font-semibold mb-3">Analysis Results:</h4>
              
              {/* Basic Stats */}
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
                <div className="text-center">
                  <div className="text-2xl font-bold text-blue-400">{analyzeResult.analysis.word_count}</div>
                  <div className="text-sm text-gray-400">Words</div>
                </div>
                <div className="text-center">
                  <div className="text-2xl font-bold text-green-400">{analyzeResult.analysis.sentence_count}</div>
                  <div className="text-sm text-gray-400">Sentences</div>
                </div>
                <div className="text-center">
                  <div className="text-2xl font-bold text-purple-400">{analyzeResult.analysis.embedding_stats.dimension}</div>
                  <div className="text-sm text-gray-400">Dimensions</div>
                </div>
                <div className="text-center">
                  <div className="text-2xl font-bold text-yellow-400">{(analyzeResult.processing_time * 1000).toFixed(0)}ms</div>
                  <div className="text-sm text-gray-400">Processing</div>
                </div>
              </div>
              
              {/* Agreement Features */}
              {analyzeResult.analysis.agreement_features && (
                <div className="border-t border-gray-600 pt-4">
                  <h5 className="font-semibold mb-2">Influencer Agreement Features:</h5>
                  
                  <div className="grid grid-cols-2 gap-4 mb-3">
                    <div>
                      <div className="text-sm text-gray-400">Agreement Score:</div>
                      <div className="flex items-center gap-2">
                        <div className="flex-1 bg-gray-700 rounded-full h-2">
                          <div 
                            className="bg-blue-500 h-2 rounded-full"
                            style={{ width: `${analyzeResult.analysis.agreement_features.agreement_score * 100}%` }}
                          ></div>
                        </div>
                        <span className="text-sm font-mono">
                          {(analyzeResult.analysis.agreement_features.agreement_score * 100).toFixed(0)}%
                        </span>
                      </div>
                    </div>
                  </div>
                  
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-2 text-sm">
                    <div className={`p-2 rounded ${analyzeResult.analysis.agreement_features.has_brand_terms ? 'bg-green-900' : 'bg-red-900'}`}>
                      Brand Terms: {analyzeResult.analysis.agreement_features.brand_term_count}
                    </div>
                    <div className={`p-2 rounded ${analyzeResult.analysis.agreement_features.has_content_terms ? 'bg-green-900' : 'bg-red-900'}`}>
                      Content Terms: {analyzeResult.analysis.agreement_features.content_term_count}
                    </div>
                    <div className={`p-2 rounded ${analyzeResult.analysis.agreement_features.has_legal_terms ? 'bg-green-900' : 'bg-red-900'}`}>
                      Legal Terms: {analyzeResult.analysis.agreement_features.legal_term_count}
                    </div>
                    <div className={`p-2 rounded ${analyzeResult.analysis.agreement_features.has_timeline_terms ? 'bg-green-900' : 'bg-red-900'}`}>
                      Timeline Terms: {analyzeResult.analysis.agreement_features.timeline_term_count}
                    </div>
                  </div>
                </div>
              )}
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default ModelTester;

