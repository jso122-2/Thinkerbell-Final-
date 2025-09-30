# Thinkerbell Legal Text Generator

🤖 **Intelligent Legal Document Generation with Auto-Detection**

Transform rough legal text examples into professional, comprehensive legal templates using AI-powered analysis and generation.

## ✨ Features

- **🤖 Smart Auto-Detection**: Automatically detects document type, style, and optimal length
- **📦 Batch Processing**: Process multiple documents simultaneously with progress tracking
- **📄 Professional Output**: Download results as organized .txt files or ZIP archives
- **⚡ Real-Time Analysis**: Live parameter detection as you type
- **🎨 Multiple Styles**: Professional, formal, business, and detailed options
- **📊 Performance Metrics**: 96.4% accuracy, 84.5% Recall@5

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- pip or conda
- 4GB+ RAM (for model loading)

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd Thinkerbell
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements/prod.txt
   ```

3. **Start the application**
   ```bash
   # Option 1: Backend + HTML Webapp (Recommended)
   ./start_backend_only.sh
   # Then open simple_webapp.html in your browser
   
   # Option 2: Full-stack with React frontend
   ./start_fullstack.sh
   ```

4. **Access the application**
   - **HTML Webapp**: Open `simple_webapp.html` in your browser
   - **API Documentation**: http://localhost:8000/docs
   - **React Frontend**: http://localhost:5173 (if using full-stack)

## 📖 Usage

### Single Document Generation

1. Open the webapp
2. Enter your legal text example (50+ characters recommended)
3. Watch parameters auto-detect in real-time
4. Click "Generate Legal Template"
5. Download your professional legal document

### Batch Processing

1. Navigate to "Batch Processing"
2. Add multiple text examples
3. Each input gets individually auto-detected
4. Start batch processing
5. Download organized ZIP file with all results

## 🏗️ Architecture

```
Thinkerbell/
├── backend_api_server.py      # FastAPI backend with auto-detection
├── simple_webapp.html         # Enhanced HTML webapp
├── models/                    # AI models
├── requirements/              # Dependencies
├── docs/                      # Documentation
├── config/                    # Configuration files
├── docker/                    # Docker deployment
└── scripts/                   # Deployment scripts
```

## 🔧 Configuration

### Environment Variables

- `THINKERBELL_MODEL_DIR`: Path to model directory (default: `./models/thinkerbell-encoder-best`)
- `PORT`: API server port (default: 8000)
- `HOST`: API server host (default: 0.0.0.0)

### Model Configuration

The system uses a fine-tuned sentence transformer model optimized for legal text generation. The model is automatically loaded on startup.

## 📊 API Endpoints

- `GET /health` - Health check and model status
- `POST /generate` - Single text generation
- `POST /auto-detect` - Auto-detect parameters from text
- `POST /batch/generate` - Start batch processing
- `GET /batch/status/{id}` - Check batch status
- `GET /batch/download/{id}` - Download batch results
- `GET /batch/list` - List all batch jobs

## 🐳 Docker Deployment

```bash
# Build and run with Docker
make build
make prod

# Or use Docker Compose directly
docker-compose up -d
```

## 📝 Development

Development files, training scripts, and additional documentation are archived at:
```
/home/black-cat/Documents/archive/Thinkerbell_archive/
```

This external archive contains all development tools, training data, and comprehensive documentation while keeping the production codebase clean.

## 🤝 Support

- **Documentation**: See `docs/` directory
- **Issues**: Create GitHub issues for bugs or feature requests
- **API Docs**: Visit `/docs` endpoint when server is running

## 📄 License

© 2025 Thinkerbell Legal Text Generator

---

**"Where scientific enquiry meets hardcore creativity – Measured Magic"**
# Thinkerbell-Final-
