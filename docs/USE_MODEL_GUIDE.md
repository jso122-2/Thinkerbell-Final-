# 🚀 Thinkerbell "Use Model" Feature Guide

## Overview

The new "Use Model" functionality allows clients to transform rough, human-written legal text examples into professional, comprehensive legal templates. This tool is designed to save time for clients who previously wrote their own templates manually.

## Features

### ⚖️ Legal Text Generator
- **Input**: 600-800 word human-written examples in plain language
- **Output**: Professional legal templates with proper structure and completeness
- **Customization**: Adjustable length, style, and document type
- **Analysis**: Similarity scoring and metadata about the generation process

## How to Use

### 1. Start the Backend Server
```bash
cd /home/black-cat/Documents/Thinkerbell
python backend_api_server.py
```

### 2. Start the Frontend
```bash
cd /home/black-cat/Documents/Thinkerbell/thinkerbell
npm run dev
```

### 3. Access the Application
- Open your browser to `http://localhost:5173`
- Click "⚖️ Use Model to Generate Legal Text"

### 4. Generate Legal Templates
1. **Enter your human example**: Describe your legal agreement in plain language
2. **Configure settings**:
   - **Target Length**: 500-1200 words
   - **Style**: Professional, Formal Legal, Business Casual, or Highly Detailed
   - **Document Type**: Legal Template, Influencer Agreement, Brand Partnership, etc.
3. **Click "Generate Legal Template"**
4. **Review results**: Compare original vs generated text, check similarity score

## Example Input

```
I need a contract for working with an Instagram influencer. They will post about our skincare products twice a week for 2 months. We'll pay them $2000 plus send free products. They need to use our hashtags and mention our brand. The posts should look natural and fit their style. We want to track how many people click on their posts and buy our products. The influencer can't work with competing skincare brands during this time. We need to make sure they follow advertising rules and say it's a paid partnership.
```

## Example Output

The model will generate a comprehensive legal template like:

```
INFLUENCER MARKETING AGREEMENT

This agreement between [Brand Name] and [Content Creator] establishes the comprehensive terms for a strategic marketing collaboration. The creator agrees to develop authentic content featuring brand products across Instagram platforms. Content deliverables include posts, stories, video content with proper brand attribution and hashtag usage. All content must align with brand guidelines while maintaining the creator's authentic voice and style.

The collaboration period spans 60 days with exclusive content rights during this timeframe. Compensation includes monetary compensation plus product gifting as outlined in the attached rate card. Usage rights extend to brand marketing materials and promotional campaigns with proper creator attribution.

Performance will be measured through comprehensive analytics including engagement rates, reach, impressions, and conversion tracking. Both parties commit to transparent reporting and data sharing to optimize campaign effectiveness and ensure mutual success.
```

## API Endpoints

### POST /generate
Generate similar legal text based on human example.

**Request:**
```json
{
  "human_example": "Your plain language description...",
  "target_length": 700,
  "style_preference": "professional",
  "document_type": "legal_template"
}
```

**Response:**
```json
{
  "generated_text": "LEGAL TEMPLATE...",
  "similarity_to_example": 0.85,
  "word_count": 687,
  "processing_time": 1.234,
  "generation_metadata": {
    "style_preference": "professional",
    "document_type": "legal_template",
    "reference_templates_used": 3,
    "target_length": 700,
    "actual_length": 687
  }
}
```

## Testing

### Quick Test Script
```bash
python test_generate_endpoint.py
```

### Manual Testing
1. Use the web interface at `http://localhost:5173`
2. Click "Load Sample" to populate with example data
3. Adjust settings and generate templates
4. Compare results using the comparison view

## Tips for Better Results

- **Be specific**: Include details like duration, compensation, deliverables, and restrictions
- **Mention platforms**: Specify Instagram, TikTok, YouTube, etc.
- **Include metrics**: Describe how success will be measured
- **Add context**: Explain the relationship between parties and their responsibilities
- **Use examples**: The more context you provide, the better the generated template

## Technical Details

### Model Integration
- Uses the trained Thinkerbell sentence transformer model
- Leverages semantic similarity to find relevant template patterns
- Combines multiple reference templates to generate comprehensive output
- Maintains semantic similarity to original intent while adding professional structure

### Generation Process
1. **Analysis**: Extract key terms and concepts from human example
2. **Template Matching**: Find most similar legal templates from training data
3. **Structure Generation**: Create professional document structure
4. **Content Synthesis**: Combine patterns while preserving original intent
5. **Length Adjustment**: Scale to target word count
6. **Quality Assessment**: Calculate similarity score and metadata

## Troubleshooting

### Backend Issues
- Ensure model is loaded: Check health endpoint shows `model_loaded: true`
- Verify dependencies: Install `sentence-transformers` and `torch`
- Check model path: Ensure model exists at specified location

### Frontend Issues
- Verify backend is running on port 8000
- Check browser console for API errors
- Ensure CORS is properly configured

### Generation Issues
- Provide more detailed input (minimum 50 characters)
- Try different style preferences
- Adjust target length for better results
- Check similarity score - low scores may indicate need for more context

## Future Enhancements

- **Template Library**: Pre-built templates for common use cases
- **Multi-language Support**: Generate templates in different languages
- **Advanced Customization**: More granular control over generation parameters
- **Batch Processing**: Generate multiple templates at once
- **Export Options**: PDF, Word document, and other format exports

