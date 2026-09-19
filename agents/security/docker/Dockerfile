# ==============================================================================
# Security Agent Dockerfile (Tier 2 - Vulnerability & Patch Operator)
# ==============================================================================

FROM python:3.12-slim

WORKDIR /app

# Install system dependencies & Trivy vulnerability scanner
RUN apt-get update && apt-get install -y --no-install-recommends \
    wget \
    curl \
    git \
    jq \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Install Trivy
RUN wget -qO - https://aquasecurity.github.io/trivy-repo/deb/public.key | gpg --dearmor -o /usr/share/keyrings/trivy.gpg && \
    echo "deb [signed-by=/usr/share/keyrings/trivy.gpg] https://aquasecurity.github.io/trivy-repo/deb generic main" | tee /etc/apt/sources.list.d/trivy.list && \
    apt-get update && \
    apt-get install -y --no-install-recommends trivy && \
    rm -rf /var/lib/apt/lists/*

# Copy requirements first for build caching
COPY agents/security/docker/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# Copy agent source code and policies
COPY agents/security/src/ /app/src/
COPY agents/shared/ /app/shared/
COPY policies/ /app/policies/

ENV PYTHONPATH=/app:/app/shared

# Data directory permissions for non-root user (UID 65534)
RUN mkdir -p /var/scan-results /tmp && \
    chown -R 65534:65534 /app /var/scan-results /tmp

USER 65534

# Health check
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8080/health')" || exit 1

EXPOSE 8080 9090

CMD ["python", "-m", "src.handlers.api_server"]
