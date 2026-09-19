# ==============================================================================
# IT-Ops Agent Dockerfile (Tier 3 - Operations & Maintenance Operator)
# ==============================================================================

FROM python:3.12-slim

WORKDIR /app

# Install system dependencies & kubectl
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    git \
    jq \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Install kubectl
RUN curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl" && \
    chmod +x kubectl && \
    mv kubectl /usr/local/bin/

# Copy requirements first for caching
COPY agents/it-ops/docker/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# Copy agent source code and policies
COPY agents/it-ops/src/ /app/src/
COPY agents/shared/ /app/shared/
COPY policies/ /app/policies/

ENV PYTHONPATH=/app:/app/shared

# Permissions for non-root user (UID 65534)
RUN mkdir -p /var/ops-data /tmp && \
    chown -R 65534:65534 /app /var/ops-data /tmp

USER 65534

# Health check
HEALTHCHECK --interval=15s --timeout=5s --start-period=10s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8080/health')" || exit 1

EXPOSE 8080 9090

CMD ["python", "-m", "src.handlers.api_server"]
