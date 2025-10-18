# IT-Ops Agent Dockerfile
# Tier 3 - IT operations automation and incident response

FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    git \
    jq \
    kubectl \
    && rm -rf /var/lib/apt/lists/*

# Install kubectl
RUN curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl" && \
    chmod +x kubectl && \
    mv kubectl /usr/local/bin/

# Copy requirements first for better caching
COPY agents/it-ops/docker/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# Copy agent source code
COPY agents/it-ops/src/ /app/src/

# Copy framework policies and configurations
COPY framework/policies/ /app/framework/policies/
COPY framework/frameworks/ /app/framework/frameworks/

# Create non-root user
RUN useradd -m -u 1000 it-ops-agent && \
    chown -R it-ops-agent:it-ops-agent /app

# Create data directories
RUN mkdir -p /var/ops-data /tmp && \
    chown -R it-ops-agent:it-ops-agent /var/ops-data /tmp

USER it-ops-agent

# Health check
HEALTHCHECK --interval=15s --timeout=5s --start-period=10s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8080/health')" || exit 1

# Expose ports
EXPOSE 8080 9090

# Long-running API server
CMD ["python", "-m", "src.handlers.api_server"]
