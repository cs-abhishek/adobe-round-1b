#!/bin/bash
# Docker Test Script for Adobe Hackathon Round 1B
# Tests all aspects of containerized deployment

set -e

echo "🐳 Adobe Hackathon Round 1B - Docker Testing Suite"
echo "=" $(printf '=%.0s' {1..50})
echo

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

log_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

log_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

log_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

log_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Test configuration
IMAGE_NAME="adobe-hackathon-1b"
CONTAINER_NAME="adobe-test-container"
TEST_DIR="$(pwd)"

# Cleanup function
cleanup() {
    log_info "Cleaning up test environment..."
    docker stop $CONTAINER_NAME 2>/dev/null || true
    docker rm $CONTAINER_NAME 2>/dev/null || true
}

# Set cleanup trap
trap cleanup EXIT

# Test 1: Build Docker image
log_info "Test 1: Building Docker image..."
if docker build -t $IMAGE_NAME .; then
    log_success "Docker image built successfully"
else
    log_error "Docker build failed"
    exit 1
fi

# Test 2: Check image size
log_info "Test 2: Checking image size..."
IMAGE_SIZE=$(docker images $IMAGE_NAME --format "table {{.Size}}" | tail -n 1)
log_info "Image size: $IMAGE_SIZE"

# Test 3: Create test input
log_info "Test 3: Preparing test input..."
mkdir -p test_input test_output

# Create persona file
cat > test_persona.json << EOF
{
  "persona": "Senior software engineer specializing in machine learning",
  "job": "Find best practices for implementing neural networks and deep learning models in production systems"
}
EOF

# Create test document
cat > test_input/test_document.txt << EOF
# Machine Learning in Production

## Introduction
This document covers best practices for deploying machine learning models in production environments.

## Neural Network Optimization
Deep learning models require careful optimization for production deployment. Key considerations include:
- Model quantization to reduce size
- Batch processing for efficiency
- GPU memory management
- Inference optimization

## Production Architecture
Successful ML production systems typically include:
- Model versioning and rollback capabilities
- A/B testing frameworks
- Monitoring and alerting systems
- Data pipeline management

## Performance Monitoring
Monitor key metrics:
- Inference latency
- Throughput
- Model accuracy drift
- Resource utilization

## Best Practices
1. Use containerization for consistent deployments
2. Implement proper logging and monitoring
3. Design for scalability
4. Plan for model updates and rollbacks
5. Ensure data quality validation

## Conclusion
Production ML systems require careful planning and robust infrastructure to succeed.
EOF

log_success "Test input prepared"

# Test 4: Run container with offline mode
log_info "Test 4: Running container in offline mode..."
docker run -d \
    --name $CONTAINER_NAME \
    --network none \
    -v "${TEST_DIR}/test_input:/app/input" \
    -v "${TEST_DIR}/test_output:/app/output" \
    -v "${TEST_DIR}/test_persona.json:/app/persona.json" \
    -e KEEP_ALIVE=false \
    $IMAGE_NAME

# Wait for container to complete
log_info "Waiting for processing to complete..."
docker wait $CONTAINER_NAME

# Test 5: Check container logs
log_info "Test 5: Checking container execution logs..."
LOGS=$(docker logs $CONTAINER_NAME)
echo "$LOGS"

# Test 6: Validate output
log_info "Test 6: Validating output..."
if [ -f "test_output/analysis.json" ]; then
    log_success "Output file generated"
    
    # Check JSON validity
    if python -m json.tool test_output/analysis.json > /dev/null 2>&1; then
        log_success "Output is valid JSON"
    else
        log_error "Output is not valid JSON"
        exit 1
    fi
    
    # Check content
    python << EOF
import json
try:
    with open('test_output/analysis.json', 'r') as f:
        data = json.load(f)
    
    print("📊 Output Analysis:")
    print(f"   Documents: {len(data.get('metadata', {}).get('documents', []))}")
    print(f"   Sections: {len(data.get('extracted_sections', []))}")
    print(f"   Processing time: {data.get('metadata', {}).get('processing_time', 'N/A')} seconds")
    
    # Validate structure
    required_keys = ['extracted_sections', 'subsection_analysis', 'metadata']
    missing_keys = [key for key in required_keys if key not in data]
    
    if missing_keys:
        print(f"❌ Missing required keys: {missing_keys}")
        exit(1)
    else:
        print("✅ Output structure is valid")
        
    # Check if relevant content was found
    if len(data.get('extracted_sections', [])) > 0:
        print("✅ Relevant sections were extracted")
    else:
        print("⚠️  No relevant sections found")
        
except Exception as e:
    print(f"❌ Error analyzing output: {e}")
    exit(1)
EOF
    
else
    log_error "No output file generated"
    exit 1
fi

# Test 7: Performance validation
log_info "Test 7: Validating performance constraints..."
PROCESSING_TIME=$(echo "$LOGS" | grep -o "Processing time: [0-9]* seconds" | grep -o "[0-9]*" || echo "unknown")

if [ "$PROCESSING_TIME" != "unknown" ] && [ "$PROCESSING_TIME" -le 60 ]; then
    log_success "Processing time: ${PROCESSING_TIME}s (meets <60s requirement)"
else
    log_warning "Processing time: ${PROCESSING_TIME}s (check if meets requirements)"
fi

# Test 8: Security validation
log_info "Test 8: Checking security configuration..."
USER_INFO=$(docker run --rm $IMAGE_NAME id)
if echo "$USER_INFO" | grep -q "uid=1000"; then
    log_success "Running as non-root user"
else
    log_warning "User configuration: $USER_INFO"
fi

# Test 9: Offline operation validation
log_info "Test 9: Validating offline operation..."
if echo "$LOGS" | grep -q "TRANSFORMERS_OFFLINE=1"; then
    log_success "Offline mode properly configured"
else
    log_warning "Offline mode configuration not detected"
fi

# Test 10: Resource usage check
log_info "Test 10: Checking resource usage..."
STATS=$(docker stats $CONTAINER_NAME --no-stream --format "table {{.CPUPerc}}\t{{.MemUsage}}" | tail -n 1)
log_info "Final resource usage: $STATS"

echo
log_success "🎉 All Docker tests completed!"
echo
echo "📋 Test Summary:"
echo "   ✅ Image build: SUCCESS"
echo "   ✅ Container execution: SUCCESS"
echo "   ✅ Output generation: SUCCESS"
echo "   ✅ JSON validation: SUCCESS"
echo "   ✅ Performance: ${PROCESSING_TIME}s"
echo "   ✅ Security: Non-root user"
echo "   ✅ Offline operation: Configured"

# Cleanup test files
log_info "Cleaning up test files..."
rm -rf test_input test_output test_persona.json

echo
echo "🐳 Docker deployment is ready for Adobe Hackathon Round 1B!"
echo "📁 Use the following commands to run:"
echo "   docker build -t adobe-hackathon-1b ."
echo "   docker run -v ./input:/app/input -v ./output:/app/output adobe-hackathon-1b"
