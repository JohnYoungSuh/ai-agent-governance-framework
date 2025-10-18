# Architect Agent Dockerfile
# Tier 4 - System design and architectural decisions

FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    git \
    graphviz \
    plantuml \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY agents/architect/docker/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# Copy agent source code
COPY agents/architect/src/ /app/src/

# Copy framework policies and configurations
COPY framework/policies/ /app/framework/policies/
COPY framework/frameworks/ /app/framework/frameworks/

# Create non-root user
RUN useradd -m -u 1000 architect-agent && \
    chown -R architect-agent:architect-agent /app

# Create data directories
RUN mkdir -p /var/design-artifacts /var/design-artifacts/diagrams /var/design-artifacts/adr /tmp && \
    chown -R architect-agent:architect-agent /var/design-artifacts /tmp

USER architect-agent

# Health check
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8080/health')" || exit 1

# Expose ports
EXPOSE 8080 9090

# Long-running API server
CMD ["python", "-m", "src.handlers.api_server"]
