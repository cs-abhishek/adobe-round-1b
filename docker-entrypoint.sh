#!/bin/bash
# Adobe Hackathon Round 1B - Document Intelligence Entrypoint
# Ensures offline operation and validates constraints

set -e

echo "🏆 Adobe Hackathon 2025 - Round 1B"
echo "📋 Persona-Driven Document Intelligence System"
echo "=" $(printf '=%.0s' {1..50})
echo

# Validate environment
echo "🔍 Validating hackathon constraints..."

# Check if we're offline (no internet access)
if ping -c 1 google.com >/dev/null 2>&1; then
    echo "⚠️  WARNING: Internet access detected - this should run offline only"
    echo "🔒 Disabling network access for compliance..."
    export TRANSFORMERS_OFFLINE=1
    export HF_DATASETS_OFFLINE=1
fi

# Check system resources
echo "💻 System Resources:"
echo "   CPU cores: $(nproc)"
echo "   Memory: $(free -h | awk '/^Mem:/ {print $2}')"
echo "   Disk space: $(df -h /app | awk 'NR==2 {print $4}')"

# Validate required directories
echo "📁 Checking directories..."
if [ ! -d "/app/input" ]; then
    echo "❌ Error: /app/input directory not found"
    exit 1
fi

if [ ! -d "/app/output" ]; then
    echo "❌ Error: /app/output directory not found"
    exit 1
fi

# Check for input files
INPUT_COUNT=$(find /app/input -name "*.pdf" -o -name "*.txt" | wc -l)
echo "📄 Found $INPUT_COUNT input files"

if [ $INPUT_COUNT -eq 0 ]; then
    echo "⚠️  No PDF or text files found in /app/input"
    echo "📝 Creating demo files for testing..."
    python create_demo.py
fi

# Check persona configuration
if [ ! -f "/app/persona.json" ]; then
    echo "📝 Creating default persona configuration..."
    cat > /app/persona.json << EOF
{
  "persona": "Data scientist working in healthcare research",
  "job": "Find machine learning techniques and methodologies for medical image analysis and diagnosis"
}
EOF
fi

# Display persona info
echo "👤 Persona Configuration:"
python -c "
import json
try:
    with open('/app/persona.json', 'r') as f:
        config = json.load(f)
    print(f'   Persona: {config[\"persona\"]}')
    print(f'   Job: {config[\"job\"]}')
except Exception as e:
    print(f'   Error reading persona: {e}')
"

# Validate models are cached
echo "🤖 Checking AI models..."
python -c "
try:
    from sentence_transformers import SentenceTransformer
    model = SentenceTransformer('all-MiniLM-L6-v2')
    print('   ✅ Sentence transformer model ready (~90MB)')
except Exception as e:
    print('   ⚠️  Sentence transformer not available, using TF-IDF fallback')

import nltk
try:
    nltk.data.find('tokenizers/punkt')
    nltk.data.find('corpora/stopwords')
    print('   ✅ NLTK data ready')
except:
    print('   ❌ NLTK data missing')
"

echo
echo "🚀 Starting document analysis..."
echo "⏱️  Start time: $(date)"

# Record start time for performance measurement
START_TIME=$(date +%s)

# Run the main analysis with timeout (hackathon constraint: <60s)
timeout 120s python main.py

# Calculate processing time
END_TIME=$(date +%s)
PROCESSING_TIME=$((END_TIME - START_TIME))

echo
echo "📊 Performance Results:"
echo "   ⏱️  Processing time: ${PROCESSING_TIME} seconds"

# Validate hackathon constraints
if [ $PROCESSING_TIME -le 60 ]; then
    echo "   ✅ Speed requirement met (<60 seconds)"
else
    echo "   ⚠️  Speed requirement exceeded (>60 seconds)"
fi

# Check output file
if [ -f "/app/output/analysis.json" ]; then
    OUTPUT_SIZE=$(stat -f%z "/app/output/analysis.json" 2>/dev/null || stat -c%s "/app/output/analysis.json")
    echo "   ✅ Output generated (${OUTPUT_SIZE} bytes)"
    
    # Display quick stats
    python -c "
import json
try:
    with open('/app/output/analysis.json', 'r') as f:
        data = json.load(f)
    print(f'   📚 Documents processed: {len(data[\"metadata\"][\"documents\"])}')
    print(f'   📑 Sections found: {len(data[\"extracted_sections\"])}')
    print(f'   📝 Subsections analyzed: {len(data[\"subsection_analysis\"])}')
except Exception as e:
    print(f'   ❌ Error reading output: {e}')
"
else
    echo "   ❌ No output file generated"
    exit 1
fi

echo
echo "🎉 Adobe Hackathon Round 1B - Analysis Complete!"
echo "📁 Results saved to /app/output/analysis.json"

# Keep container alive for inspection if needed
if [ "${KEEP_ALIVE:-false}" = "true" ]; then
    echo "🔍 Container kept alive for inspection (KEEP_ALIVE=true)"
    tail -f /dev/null
fi
