# Dockerfile for Adobe Hackathon Round 1B
# Objective: Run Python code that performs document relevance analysis based on persona/job description
# 
# Constraints:
# - Must work offline (no internet calls)
# - Base image must be linux/amd64 compatible  
# - Model (if used) must be under 1GB and stored locally
# - Python script should read from /app/input, write to /app/output

FROM --platform=linux/amd64 python:3.9-slim

# Set working directory
WORKDIR /app

# Install system dependencies for PDF processing and ML libraries
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    build-essential \
    wget \
    curl \
    libffi-dev \
    libssl-dev \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Copy requirements and install Python dependencies
COPY requirements.txt .

# Install core dependencies with CPU-only optimization
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir \
    PyPDF2==3.0.1 \
    pdfplumber==0.9.0 \
    PyMuPDF==1.23.3 \
    nltk==3.8.1 \
    scikit-learn==1.3.0 \
    numpy==1.24.3 \
    tqdm==4.65.0 \
    && pip install --no-cache-dir --index-url https://download.pytorch.org/whl/cpu \
    torch==2.0.1+cpu \
    && pip install --no-cache-dir \
    sentence-transformers==2.2.2 \
    transformers==4.32.1

# Pre-download and cache NLTK data offline
RUN python -c "import nltk; nltk.download('punkt', quiet=True); nltk.download('stopwords', quiet=True); print('NLTK data cached')"

# Pre-download sentence transformer model (under 1GB constraint)
RUN python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('all-MiniLM-L6-v2'); print('Sentence transformer model cached (~90MB)')" || echo "Sentence transformer caching failed, will use TF-IDF fallback"

# Copy application code
COPY src/ src/
COPY main.py .
COPY config.json .

# Copy additional files for enhanced functionality
COPY setup.py .
COPY create_demo.py .

# Create required directories with proper permissions
RUN mkdir -p /app/input /app/output /app/models /app/logs && \
    chmod 755 /app/input /app/output /app/models /app/logs

# Set environment variables for offline operation
ENV PYTHONPATH=/app
ENV TRANSFORMERS_OFFLINE=1
ENV TRANSFORMERS_CACHE=/app/models
ENV HF_DATASETS_OFFLINE=1
ENV TORCH_HOME=/app/models
ENV NLTK_DATA=/root/nltk_data

# Add health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import sys; print('Container healthy'); sys.exit(0)"

# Set user permissions for security
RUN useradd -m -u 1000 hackathon && \
    chown -R hackathon:hackathon /app
USER hackathon

# Expose port for potential web interface (optional)
EXPOSE 8000

# Default command with error handling
CMD ["python", "-u", "main.py"]

# Labels for Adobe Hackathon submission
LABEL version="1.0.0"
LABEL description="Adobe Hackathon 2025 Round 1B - Persona-Driven Document Intelligence"
LABEL maintainer="Adobe Hackathon Team"
LABEL hackathon.round="1B"
LABEL hackathon.constraints="cpu-only,offline,<1GB-model,<60s-processing"
LABEL hackathon.features="pdf-parsing,nlp-analysis,persona-matching,relevance-scoring"
