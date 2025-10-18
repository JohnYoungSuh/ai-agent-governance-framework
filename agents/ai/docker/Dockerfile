# AI Agent Dockerfile
# Tier 3 - AI/ML model training and deployment

FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    git \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY agents/ai/docker/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# Copy agent source code
COPY agents/ai/src/ /app/src/

# Copy framework policies and configurations
COPY framework/policies/ /app/framework/policies/
COPY framework/frameworks/ /app/framework/frameworks/

# Create non-root user
RUN useradd -m -u 1000 ai-agent && \
    chown -R ai-agent:ai-agent /app

# Create data directories
RUN mkdir -p /var/ml-data /var/ml-data/models /var/ml-data/datasets /var/ml-data/checkpoints /tmp && \
    chown -R ai-agent:ai-agent /var/ml-data /tmp

USER ai-agent

# Health check
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8080/health')" || exit 1

# Expose ports
EXPOSE 8080 9090

# Default command (training job)
CMD ["python", "-m", "src.handlers.training_job"]
