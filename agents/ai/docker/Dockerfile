# ==============================================================================
# AI Agent Dockerfile (Tier 2 - Model Operator)
# ==============================================================================

FROM python:3.12-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    git \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY agents/ai/docker/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

COPY agents/ai/src/ /app/src/
COPY policies/ /app/policies/

# Permissions for non-root user (UID 65534)
RUN mkdir -p /var/ml-data /var/ml-data/models /var/ml-data/datasets /var/ml-data/checkpoints /tmp && \
    chown -R 65534:65534 /app /var/ml-data /tmp

USER 65534

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8080/health')" || exit 1

EXPOSE 8080 9090

CMD ["python", "-m", "src.handlers.training_job"]
