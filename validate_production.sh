#!/bin/bash

# Thinkerbell Production Validation Script
# Validates the production setup without installing dependencies

echo "🔍 Thinkerbell Production Validation"
echo "===================================="

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_check() {
    echo -e "${BLUE}[CHECK]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[✅]${NC} $1"
}

print_info() {
    echo -e "${YELLOW}[INFO]${NC} $1"
}

# Check directory structure
print_check "Validating production directory structure..."

required_files=(
    "backend_api_server.py"
    "simple_webapp.html"
    "deploy.sh"
    "README.md"
    "requirements_production.txt"
    "PRODUCTION_READY.md"
)

missing_files=()
for file in "${required_files[@]}"; do
    if [ -f "$file" ]; then
        print_success "Found: $file"
    else
        missing_files+=("$file")
    fi
done

if [ ${#missing_files[@]} -eq 0 ]; then
    print_success "All required files present"
else
    echo "❌ Missing files: ${missing_files[*]}"
    exit 1
fi

# Check directories
required_dirs=(
    "models"
    "docs"
    "config"
    "archive_dev_files"
)

for dir in "${required_dirs[@]}"; do
    if [ -d "$dir" ]; then
        print_success "Directory exists: $dir"
    else
        echo "⚠️  Directory missing: $dir"
    fi
done

# Check if development files were properly archived
print_check "Validating development files were archived..."

dev_files_that_should_be_gone=(
    "thinkerbell_env"
    "Thinkerbell_template_pipeline"
    "data_generation"
    "complete_pipeline_5000"
    "synthetic_dataset"
    "__pycache__"
)

archived_correctly=true
for file in "${dev_files_that_should_be_gone[@]}"; do
    if [ -e "$file" ]; then
        echo "⚠️  Development file still present: $file"
        archived_correctly=false
    fi
done

if $archived_correctly; then
    print_success "Development files properly archived"
fi

# Check archive directory
if [ -d "archive_dev_files" ]; then
    archive_count=$(find archive_dev_files -type f | wc -l)
    print_success "Archive contains $archive_count files"
else
    echo "❌ Archive directory missing"
fi

# Check script permissions
print_check "Validating script permissions..."
if [ -x "deploy.sh" ]; then
    print_success "deploy.sh is executable"
else
    echo "⚠️  deploy.sh is not executable (run: chmod +x deploy.sh)"
fi

# Check Python availability
print_check "Validating Python environment..."
if command -v python3 &> /dev/null; then
    python_version=$(python3 --version)
    print_success "Python available: $python_version"
else
    echo "❌ Python 3 not found"
    exit 1
fi

# Check model directory
print_check "Validating model availability..."
model_found=false
if [ -d "models/thinkerbell-encoder-best" ]; then
    print_success "Primary model found: thinkerbell-encoder-best"
    model_found=true
fi

if [ -d "models/optimum-model" ]; then
    print_success "Optimized model found: optimum-model"
    model_found=true
fi

if ! $model_found; then
    echo "⚠️  No models found in models/ directory"
    print_info "Models may need to be downloaded or moved from archive"
fi

# Check file sizes (basic validation)
print_check "Validating core file sizes..."

if [ -f "backend_api_server.py" ]; then
    backend_size=$(wc -c < backend_api_server.py)
    if [ $backend_size -gt 50000 ]; then
        print_success "Backend API server appears complete ($backend_size bytes)"
    else
        echo "⚠️  Backend API server seems small ($backend_size bytes)"
    fi
fi

if [ -f "simple_webapp.html" ]; then
    webapp_size=$(wc -c < simple_webapp.html)
    if [ $webapp_size -gt 80000 ]; then
        print_success "Webapp appears complete ($webapp_size bytes)"
    else
        echo "⚠️  Webapp seems small ($webapp_size bytes)"
    fi
fi

# Summary
echo ""
echo "📊 Production Validation Summary"
echo "==============================="
echo ""

# Count files in production vs archive
prod_files=$(find . -maxdepth 1 -type f | wc -l)
if [ -d "archive_dev_files" ]; then
    archive_files=$(find archive_dev_files -type f | wc -l)
else
    archive_files=0
fi

print_info "Production files: $prod_files"
print_info "Archived files: $archive_files"

# Calculate space saved
if [ -d "archive_dev_files" ]; then
    archive_size=$(du -sh archive_dev_files 2>/dev/null | cut -f1)
    print_info "Space archived: $archive_size"
fi

echo ""
print_success "Production validation complete!"
echo ""
echo "🚀 Ready to deploy:"
echo "   ./deploy.sh"
echo ""
echo "📖 Read the guide:"
echo "   cat PRODUCTION_READY.md"
echo ""
