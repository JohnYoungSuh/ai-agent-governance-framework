# Security Agent Dockerfile
# Tier 3 - Security scanning and compliance checking

FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies for security tools
RUN apt-get update && apt-get install -y \
    wget \
    curl \
    git \
    jq \
    && rm -rf /var/lib/apt/lists/*

# Install Trivy (vulnerability scanner)
RUN wget -qO - https://aquasecurity.github.io/trivy-repo/deb/public.key | apt-key add - && \
    echo "deb https://aquasecurity.github.io/trivy-repo/deb $(lsb_release -sc) main" | tee -a /etc/apt/sources.list.d/trivy.list && \
    apt-get update && \
    apt-get install -y trivy && \
    rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY agents/security/docker/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# Copy agent source code
COPY agents/security/src/ /app/src/

# Copy framework policies and configurations
COPY framework/policies/ /app/framework/policies/
COPY framework/frameworks/ /app/framework/frameworks/

# Create non-root user
RUN useradd -m -u 1000 security-agent && \
    chown -R security-agent:security-agent /app

# Create data directories
RUN mkdir -p /var/scan-results /tmp && \
    chown -R security-agent:security-agent /var/scan-results /tmp

USER security-agent

# Health check
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8080/health')" || exit 1

# Expose ports
EXPOSE 8080 9090

# Default command (can be overridden for CronJob vs Deployment)
CMD ["python", "-m", "src.handlers.api_server"]
