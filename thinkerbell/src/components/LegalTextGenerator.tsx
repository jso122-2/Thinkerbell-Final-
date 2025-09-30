import React, { useState, useEffect } from 'react';
import apiService, { GenerateRequest, GenerateResponse, HealthResponse } from '../services/api';

interface LegalTextGeneratorProps {
  className?: string;
}

const LegalTextGenerator: React.FC<LegalTextGeneratorProps> = ({ className = '' }) => {
  const [health, setHealth] = useState<HealthResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  
  // Form state
  const [humanExample, setHumanExample] = useState('');
  const [targetLength, setTargetLength] = useState(700);
  const [stylePreference, setStylePreference] = useState('professional');
  const [documentType, setDocumentType] = useState('legal_template');
  
  // Results state
  const [generateResult, setGenerateResult] = useState<GenerateResponse | null>(null);
  const [showComparison, setShowComparison] = useState(false);

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

  const generateText = async () => {
    if (!humanExample.trim()) {
      setError('Please enter a human example');
      return;
    }

    if (humanExample.trim().length < 50) {
      setError('Please provide a more detailed example (at least 50 characters)');
      return;
    }

    setLoading(true);
    setError(null);
    
    try {
      const request: GenerateRequest = {
        human_example: humanExample,
        target_length: targetLength,
        style_preference: stylePreference,
        document_type: documentType
      };
      
      const result = await apiService.generate(request);
      setGenerateResult(result);
      setShowComparison(false);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Text generation failed');
    } finally {
      setLoading(false);
    }
  };

  const loadSampleExample = () => {
    setHumanExample(`I need a contract for working with an Instagram influencer. They will post about our skincare products twice a week for 2 months. We'll pay them $2000 plus send free products. They need to use our hashtags and mention our brand. The posts should look natural and fit their style. We want to track how many people click on their posts and buy our products. The influencer can't work with competing skincare brands during this time. We need to make sure they follow advertising rules and say it's a paid partnership.`);
    setTargetLength(650);
    setStylePreference('professional');
    setDocumentType('legal_template');
  };

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text).then(() => {
      // Could add a toast notification here
    });
  };

  const getSimilarityColor = (similarity: number) => {
    if (similarity > 0.8) return 'text-green-400';
    if (similarity > 0.6) return 'text-yellow-400';
    if (similarity > 0.4) return 'text-orange-400';
    return 'text-red-400';
  };

  const getSimilarityLabel = (similarity: number) => {
    if (similarity > 0.8) return 'Excellent Match';
    if (similarity > 0.6) return 'Good Match';
    if (similarity > 0.4) return 'Fair Match';
    return 'Different Style';
  };

  return (
    <div className={`bg-gray-900 text-white p-6 rounded-lg ${className}`}>
      {/* Header */}
      <div className="mb-6">
        <h2 className="text-3xl font-bold mb-2">⚖️ Legal Text Generator</h2>
        <p className="text-gray-300 mb-4">
          Transform your rough ideas into professional legal templates. Input your human-written example 
          and get a polished, comprehensive legal document that maintains your intent while adding 
          professional structure and completeness.
        </p>
        
        {/* Health Status */}
        <div className="flex items-center gap-4 mb-4">
          <button 
            onClick={checkHealth}
            className="px-3 py-1 bg-blue-600 hover:bg-blue-700 rounded text-sm"
          >
            Check Model Status
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

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Input Section */}
        <div className="space-y-4">
          <div className="flex justify-between items-center">
            <h3 className="text-xl font-semibold">📝 Your Human Example</h3>
            <button
              onClick={loadSampleExample}
              className="px-3 py-1 bg-green-600 hover:bg-green-700 rounded text-sm"
            >
              Load Sample
            </button>
          </div>
          
          <div>
            <label className="block text-sm font-medium mb-2">
              Rough Example (600-800 words recommended):
            </label>
            <textarea
              value={humanExample}
              onChange={(e) => setHumanExample(e.target.value)}
              className="w-full p-3 bg-gray-800 border border-gray-600 rounded resize-none"
              rows={12}
              placeholder="Describe your legal agreement in plain language. Include key terms like duration, compensation, deliverables, restrictions, and any specific requirements. The more detail you provide, the better the generated template will be..."
            />
            <div className="text-sm text-gray-400 mt-1">
              {humanExample.length} characters | {humanExample.split(' ').length} words
            </div>
          </div>

          {/* Configuration */}
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium mb-2">Target Length:</label>
              <select
                value={targetLength}
                onChange={(e) => setTargetLength(Number(e.target.value))}
                className="w-full p-2 bg-gray-800 border border-gray-600 rounded"
              >
                <option value={500}>Short (500 words)</option>
                <option value={700}>Medium (700 words)</option>
                <option value={1000}>Long (1000 words)</option>
                <option value={1200}>Comprehensive (1200 words)</option>
              </select>
            </div>
            
            <div>
              <label className="block text-sm font-medium mb-2">Style:</label>
              <select
                value={stylePreference}
                onChange={(e) => setStylePreference(e.target.value)}
                className="w-full p-2 bg-gray-800 border border-gray-600 rounded"
              >
                <option value="professional">Professional</option>
                <option value="formal">Formal Legal</option>
                <option value="business">Business Casual</option>
                <option value="detailed">Highly Detailed</option>
              </select>
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium mb-2">Document Type:</label>
            <select
              value={documentType}
              onChange={(e) => setDocumentType(e.target.value)}
              className="w-full p-2 bg-gray-800 border border-gray-600 rounded"
            >
              <option value="legal_template">Legal Template</option>
              <option value="influencer_agreement">Influencer Agreement</option>
              <option value="brand_partnership">Brand Partnership</option>
              <option value="content_creation">Content Creation Contract</option>
              <option value="marketing_agreement">Marketing Agreement</option>
            </select>
          </div>

          <button
            onClick={generateText}
            disabled={loading || !health?.model_loaded}
            className="w-full px-6 py-3 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-600 rounded font-semibold"
          >
            {loading ? 'Generating Professional Template...' : '🚀 Generate Legal Template'}
          </button>
        </div>

        {/* Results Section */}
        <div className="space-y-4">
          <div className="flex justify-between items-center">
            <h3 className="text-xl font-semibold">📄 Generated Template</h3>
            {generateResult && (
              <div className="flex gap-2">
                <button
                  onClick={() => setShowComparison(!showComparison)}
                  className="px-3 py-1 bg-purple-600 hover:bg-purple-700 rounded text-sm"
                >
                  {showComparison ? 'Hide' : 'Show'} Comparison
                </button>
                <button
                  onClick={() => copyToClipboard(generateResult.generated_text)}
                  className="px-3 py-1 bg-green-600 hover:bg-green-700 rounded text-sm"
                >
                  Copy Text
                </button>
              </div>
            )}
          </div>

          {generateResult ? (
            <div className="space-y-4">
              {/* Metrics */}
              <div className="grid grid-cols-3 gap-4 p-4 bg-gray-800 rounded">
                <div className="text-center">
                  <div className="text-2xl font-bold text-blue-400">{generateResult.word_count}</div>
                  <div className="text-sm text-gray-400">Words</div>
                </div>
                <div className="text-center">
                  <div className={`text-2xl font-bold ${getSimilarityColor(generateResult.similarity_to_example)}`}>
                    {(generateResult.similarity_to_example * 100).toFixed(0)}%
                  </div>
                  <div className="text-sm text-gray-400">Similarity</div>
                </div>
                <div className="text-center">
                  <div className="text-2xl font-bold text-green-400">
                    {(generateResult.processing_time * 1000).toFixed(0)}ms
                  </div>
                  <div className="text-sm text-gray-400">Processing</div>
                </div>
              </div>

              {/* Similarity Assessment */}
              <div className="p-3 bg-gray-800 rounded">
                <div className="flex justify-between items-center">
                  <span className="text-sm font-medium">Content Similarity:</span>
                  <span className={`text-sm font-semibold ${getSimilarityColor(generateResult.similarity_to_example)}`}>
                    {getSimilarityLabel(generateResult.similarity_to_example)}
                  </span>
                </div>
                <div className="w-full bg-gray-700 rounded-full h-2 mt-2">
                  <div 
                    className={`h-2 rounded-full ${
                      generateResult.similarity_to_example > 0.8 ? 'bg-green-500' :
                      generateResult.similarity_to_example > 0.6 ? 'bg-yellow-500' :
                      generateResult.similarity_to_example > 0.4 ? 'bg-orange-500' : 'bg-red-500'
                    }`}
                    style={{ width: `${generateResult.similarity_to_example * 100}%` }}
                  ></div>
                </div>
              </div>

              {/* Generated Text */}
              <div className="bg-gray-800 p-4 rounded">
                <pre className="whitespace-pre-wrap text-sm leading-relaxed text-gray-100">
                  {generateResult.generated_text}
                </pre>
              </div>

              {/* Comparison View */}
              {showComparison && (
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <h4 className="font-semibold mb-2 text-yellow-400">Your Original:</h4>
                    <div className="bg-gray-800 p-3 rounded max-h-96 overflow-y-auto">
                      <pre className="whitespace-pre-wrap text-sm text-gray-300">
                        {humanExample}
                      </pre>
                    </div>
                  </div>
                  <div>
                    <h4 className="font-semibold mb-2 text-green-400">Generated Template:</h4>
                    <div className="bg-gray-800 p-3 rounded max-h-96 overflow-y-auto">
                      <pre className="whitespace-pre-wrap text-sm text-gray-100">
                        {generateResult.generated_text}
                      </pre>
                    </div>
                  </div>
                </div>
              )}

              {/* Generation Metadata */}
              <div className="text-sm text-gray-400 p-3 bg-gray-800 rounded">
                <div className="grid grid-cols-2 gap-2">
                  <div>Style: {generateResult.generation_metadata.style_preference}</div>
                  <div>Type: {generateResult.generation_metadata.document_type}</div>
                  <div>Target: {generateResult.generation_metadata.target_length} words</div>
                  <div>Templates Used: {generateResult.generation_metadata.reference_templates_used}</div>
                </div>
              </div>
            </div>
          ) : (
            <div className="bg-gray-800 p-8 rounded text-center text-gray-400">
              <div className="text-4xl mb-4">📝</div>
              <p>Enter your human example and click "Generate Legal Template" to see the AI-powered professional version.</p>
              <p className="text-sm mt-2">The model will analyze your input and create a comprehensive legal document that maintains your intent while adding professional structure.</p>
            </div>
          )}
        </div>
      </div>

      {/* Usage Tips */}
      <div className="mt-8 p-4 bg-blue-900 bg-opacity-50 rounded">
        <h4 className="font-semibold mb-2">💡 Tips for Better Results:</h4>
        <ul className="text-sm space-y-1 text-gray-300">
          <li>• Include specific details like duration, compensation, deliverables, and restrictions</li>
          <li>• Mention platforms, content types, and performance metrics if applicable</li>
          <li>• Describe the relationship between parties and their responsibilities</li>
          <li>• The more context you provide, the more accurate and comprehensive the generated template will be</li>
          <li>• Review and customize the generated text to match your specific legal requirements</li>
        </ul>
      </div>
    </div>
  );
};

export default LegalTextGenerator;

