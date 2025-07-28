# Dockerfile for Adobe Hackathon Document Intelligence System
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Download NLTK data
RUN python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords')"

# Copy application code
COPY src/ src/
COPY main.py .

# Create directories
RUN mkdir -p /app/input /app/output

# Set environment variables
ENV PYTHONPATH=/app

# Default command
CMD ["python", "main.py"]
